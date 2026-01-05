from http import HTTPStatus
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from src.adapters.controllers.product_controller import ProductController
from src.adapters.presenters.interfaces.presenter_interface import PresenterInterface
from src.application.exceptions import (
    ProductAlreadyExistsException,
    ProductBusinessRuleException,
    ProductNotFoundException,
    ProductValidationException,
)


class FakePresenter(PresenterInterface):
    def present(self, data):
        return {"presented": data}

    def present_list(self, data_list):
        return {"presented_list": data_list}

    def present_error(self, error: Exception) -> dict:
        return {"error": str(error)}


class StubUseCase:
    def __init__(self, result=None, exception: Exception | None = None):
        self.result = result
        self.exception = exception
        self.calls = []

    def execute(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        if self.exception:
            raise self.exception
        return self.result


class IngredientRepoStub:
    def __init__(self, result=None):
        self.result = result or SimpleNamespace(id=1)

    def find_by_id(self, ingredient_internal_id):
        return self.result


class ProductRepoStub:
    """Placeholder repository needed only for controller wiring."""


@pytest.fixture
def presenter():
    return FakePresenter()


@pytest.fixture
def ingredient_repo():
    return IngredientRepoStub()


@pytest.fixture
def controller(presenter, ingredient_repo):
    return ProductController(ProductRepoStub(), ingredient_repo, presenter), ingredient_repo


def test_get_product_success(controller):
    ctrl, _ = controller
    ctrl.read_use_case = StubUseCase(result={"id": 1})

    response = ctrl.get_product(product_internal_id=1, include_inactive=True)

    assert response == {"presented": {"id": 1}}
    assert ctrl.read_use_case.calls[-1][1]["include_inactive"] is True


def test_get_product_not_found(controller):
    ctrl, _ = controller
    ctrl.read_use_case = StubUseCase(exception=ProductNotFoundException("missing"))

    with pytest.raises(HTTPException) as captured:
        ctrl.get_product(product_internal_id=99)

    assert captured.value.status_code == HTTPStatus.NOT_FOUND
    assert captured.value.detail["error"] == "missing"


def test_create_product_success(controller):
    ctrl, ingredient_repo = controller
    ingredient_repo.result = SimpleNamespace(id=5)
    ctrl.create_use_case = StubUseCase(result={"id": 10})

    response = ctrl.create_product(
        {
            "name": "Burger",
            "price": 10.0,
            "category": "burger",
            "sku": "SKU-1",
            "default_ingredient": [{"ingredient_internal_id": "5", "quantity": 2}],
        }
    )

    assert response == {"presented": {"id": 10}}


@pytest.mark.parametrize(
    "exc",
    [
        ProductAlreadyExistsException("exists"),
        ProductBusinessRuleException("rule"),
        ProductValidationException("invalid"),
    ],
)
def test_create_product_bad_request(controller, exc):
    ctrl, ingredient_repo = controller
    ingredient_repo.result = SimpleNamespace(id=3)
    ctrl.create_use_case = StubUseCase(exception=exc)

    with pytest.raises(HTTPException) as captured:
        ctrl.create_product({"default_ingredient": [{"ingredient_internal_id": 3}]})

    assert captured.value.status_code == HTTPStatus.BAD_REQUEST
    assert captured.value.detail["error"] == str(exc)


def test_create_product_missing_ingredient_id(controller):
    ctrl, _ = controller
    ctrl.create_use_case = StubUseCase(result={"id": 1})

    with pytest.raises(HTTPException) as captured:
        ctrl.create_product({"default_ingredient": [{}]})

    assert captured.value.status_code == HTTPStatus.BAD_REQUEST
    assert "Ingredient ID is required" in captured.value.detail["error"]


def test_create_product_ingredient_not_found(controller):
    ctrl, ingredient_repo = controller
    ingredient_repo.result = None
    ctrl.create_use_case = StubUseCase(result={"id": 1})

    with pytest.raises(HTTPException) as captured:
        ctrl.create_product({"default_ingredient": [{"ingredient_internal_id": 99}]})

    assert captured.value.status_code == HTTPStatus.BAD_REQUEST
    assert "Ingredient with ID 99 not found" in captured.value.detail["error"]


def test_update_product_success(controller):
    ctrl, ingredient_repo = controller
    ingredient_repo.result = SimpleNamespace(id=7)
    ctrl.update_use_case = StubUseCase(result={"id": 7, "name": "Updated"})

    response = ctrl.update_product(
        {
            "internal_id": 7,
            "name": "Updated",
            "price": 20.0,
            "category": "burger",
            "sku": "SKU-2",
            "default_ingredient": [{"ingredient_internal_id": 7}],
        }
    )

    assert response["presented"]["id"] == 7
    assert response["presented"]["name"] == "Updated"


def test_update_product_missing_ingredient_id(controller):
    ctrl, _ = controller
    ctrl.update_use_case = StubUseCase(result={"id": 1})

    with pytest.raises(HTTPException) as captured:
        ctrl.update_product({"default_ingredient": [{}]})

    assert captured.value.status_code == HTTPStatus.BAD_REQUEST
    assert "Ingredient ID is required" in captured.value.detail["error"]


def test_update_product_not_found(controller):
    ctrl, ingredient_repo = controller
    ingredient_repo.result = SimpleNamespace(id=9)
    ctrl.update_use_case = StubUseCase(exception=ProductNotFoundException("missing"))

    with pytest.raises(HTTPException) as captured:
        ctrl.update_product({"internal_id": 9, "default_ingredient": [{"ingredient_internal_id": 9}]})

    assert captured.value.status_code == HTTPStatus.BAD_REQUEST
    assert captured.value.detail["error"] == "missing"


def test_update_product_bad_request(controller):
    ctrl, ingredient_repo = controller
    ingredient_repo.result = SimpleNamespace(id=4)
    ctrl.update_use_case = StubUseCase(exception=ProductAlreadyExistsException("duplicate"))

    with pytest.raises(HTTPException) as captured:
        ctrl.update_product({"internal_id": 4, "default_ingredient": [{"ingredient_internal_id": 4}]})

    assert captured.value.status_code == HTTPStatus.BAD_REQUEST
    assert captured.value.detail["error"] == "duplicate"


def test_delete_product_success(controller):
    ctrl, _ = controller
    ctrl.delete_use_case = StubUseCase(result=True)

    response = ctrl.delete_product(product_internal_id=2)

    assert response["presented"]["success"] is True
    assert "soft deleted" in response["presented"]["message"]


def test_delete_product_not_found(controller):
    ctrl, _ = controller
    ctrl.delete_use_case = StubUseCase(exception=ProductNotFoundException("gone"))

    with pytest.raises(HTTPException) as captured:
        ctrl.delete_product(product_internal_id=3)

    assert captured.value.status_code == HTTPStatus.NOT_FOUND
    assert captured.value.detail["error"] == "gone"


def test_delete_product_business_rule_error(controller):
    ctrl, _ = controller
    ctrl.delete_use_case = StubUseCase(exception=ProductBusinessRuleException("blocked"))

    with pytest.raises(HTTPException) as captured:
        ctrl.delete_product(product_internal_id=4)

    assert captured.value.status_code == HTTPStatus.NOT_FOUND
    assert captured.value.detail["error"] == "blocked"


def test_list_products_success(controller):
    ctrl, _ = controller
    ctrl.list_use_case = StubUseCase(result=[{"id": 1}])

    response = ctrl.list_products(include_inactive=True)

    assert response["presented"] == [{"id": 1}]
    assert ctrl.list_use_case.calls[-1][1]["include_inactive"] is True


def test_list_products_internal_error(controller):
    ctrl, _ = controller
    ctrl.list_use_case = StubUseCase(exception=RuntimeError("fail"))

    with pytest.raises(HTTPException) as captured:
        ctrl.list_products()

    assert captured.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert captured.value.detail["error"] == "fail"


def test_get_product_by_name_success(controller):
    ctrl, _ = controller
    ctrl.list_use_case = StubUseCase(
        result=SimpleNamespace(products=[SimpleNamespace(name="Target")])
    )

    response = ctrl.get_product_by_name("Target")

    assert response["presented"].name == "Target"


def test_get_product_by_name_not_found(controller):
    ctrl, _ = controller
    ctrl.list_use_case = StubUseCase(result=[])

    with pytest.raises(HTTPException) as captured:
        ctrl.get_product_by_name("Missing")

    assert captured.value.status_code == HTTPStatus.NOT_FOUND
    assert "not found" in captured.value.detail["error"]


def test_get_product_by_name_business_rule_error(controller):
    ctrl, _ = controller
    ctrl.list_use_case = StubUseCase(exception=ProductBusinessRuleException("rule"))

    with pytest.raises(HTTPException) as captured:
        ctrl.get_product_by_name("Any")

    assert captured.value.status_code == HTTPStatus.BAD_REQUEST
    assert captured.value.detail["error"] == "rule"


def test_get_product_by_category_success(controller):
    ctrl, _ = controller
    ctrl.list_by_category_use_case = StubUseCase(result=[{"id": 1}])

    response = ctrl.get_product_by_category("burger", include_inactive=True)

    assert response["presented"] == [{"id": 1}]
    assert ctrl.list_by_category_use_case.calls[-1][1]["include_inactive"] is True


def test_get_product_by_category_not_found(controller):
    ctrl, _ = controller
    ctrl.list_by_category_use_case = StubUseCase(
        exception=ProductNotFoundException("none")
    )

    with pytest.raises(HTTPException) as captured:
        ctrl.get_product_by_category("dessert")

    assert captured.value.status_code == HTTPStatus.NOT_FOUND
    assert captured.value.detail["error"] == "none"


def test_get_product_by_category_business_rule_error(controller):
    ctrl, _ = controller
    ctrl.list_by_category_use_case = StubUseCase(
        exception=ProductBusinessRuleException("invalid")
    )

    with pytest.raises(HTTPException) as captured:
        ctrl.get_product_by_category("side")

    assert captured.value.status_code == HTTPStatus.BAD_REQUEST
    assert captured.value.detail["error"] == "invalid"


def test_get_product_by_sku_success(controller):
    ctrl, _ = controller
    ctrl.read_by_sku_use_case = StubUseCase(result={"id": 11})

    response = ctrl.get_product_by_sku("SKU-11", include_inactive=True)

    assert response["presented"] == {"id": 11}
    assert ctrl.read_by_sku_use_case.calls[-1][1]["include_inactive"] is True


def test_get_product_by_sku_not_found(controller):
    ctrl, _ = controller
    ctrl.read_by_sku_use_case = StubUseCase(
        exception=ProductNotFoundException("missing")
    )

    with pytest.raises(HTTPException) as captured:
        ctrl.get_product_by_sku("SKU-404")

    assert captured.value.status_code == HTTPStatus.NOT_FOUND
    assert captured.value.detail["error"] == "missing"


def test_get_product_by_sku_business_rule_error(controller):
    ctrl, _ = controller
    ctrl.read_by_sku_use_case = StubUseCase(
        exception=ProductBusinessRuleException("blocked")
    )

    with pytest.raises(HTTPException) as captured:
        ctrl.get_product_by_sku("SKU-BAD")

    assert captured.value.status_code == HTTPStatus.BAD_REQUEST
    assert captured.value.detail["error"] == "blocked"


def test_list_products_by_category_success(controller):
    ctrl, _ = controller
    ctrl.list_by_category_use_case = StubUseCase(result=[{"id": 2}])

    response = ctrl.list_products_by_category("drink", include_inactive=False)

    assert response["presented"] == [{"id": 2}]
    assert ctrl.list_by_category_use_case.calls[-1][1]["include_inactive"] is False


def test_list_products_by_category_not_found(controller):
    ctrl, _ = controller
    ctrl.list_by_category_use_case = StubUseCase(
        exception=ProductNotFoundException("none")
    )

    with pytest.raises(HTTPException) as captured:
        ctrl.list_products_by_category("side")

    assert captured.value.status_code == HTTPStatus.NOT_FOUND
    assert captured.value.detail["error"] == "none"


def test_list_products_by_category_business_rule_error(controller):
    ctrl, _ = controller
    ctrl.list_by_category_use_case = StubUseCase(
        exception=ProductBusinessRuleException("bad")
    )

    with pytest.raises(HTTPException) as captured:
        ctrl.list_products_by_category("burger")

    assert captured.value.status_code == HTTPStatus.BAD_REQUEST
    assert captured.value.detail["error"] == "bad"
