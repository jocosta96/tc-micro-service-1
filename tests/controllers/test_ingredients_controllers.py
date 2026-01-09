from http import HTTPStatus

import pytest
from fastapi import HTTPException

from src.adapters.controllers import ingredient_controller as ingredient_controller_module
from src.adapters.controllers.ingredient_controller import IngredientController
from src.adapters.presenters.interfaces.presenter_interface import PresenterInterface
from src.application.exceptions import (
    IngredientAlreadyExistsException,
    IngredientBusinessRuleException,
    IngredientNotFoundException,
    IngredientValidationException,
)
from src.entities.ingredient import IngredientType
from src.entities.product import ProductCategory


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


@pytest.fixture
def presenter():
    return FakePresenter()


@pytest.fixture
def controller(presenter):
    class Repo:
        """Placeholder repository; actual behavior is stubbed on use cases."""

    return IngredientController(Repo(), presenter)


def test_create_ingredient_success(controller):
    controller.create_use_case = StubUseCase(result={"id": 1})

    response = controller.create_ingredient(
        {
            "name": "Salt",
            "price": 1.0,
            "is_active": True,
            "ingredient_type": IngredientType.BREAD,
            "applies_to_burger": True,
        }
    )

    assert response == {"presented": {"id": 1}}


@pytest.mark.parametrize(
    "exc",
    [
        IngredientAlreadyExistsException("dup"),
        IngredientBusinessRuleException("rule"),
        IngredientValidationException("invalid"),
    ],
)
def test_create_ingredient_bad_request(controller, exc):
    controller.create_use_case = StubUseCase(exception=exc)

    with pytest.raises(HTTPException) as captured:
        controller.create_ingredient({})

    assert captured.value.status_code == HTTPStatus.BAD_REQUEST
    assert captured.value.detail["error"] == str(exc)


def test_get_ingredient_success(controller):
    controller.read_use_case = StubUseCase(result={"id": 5})

    response = controller.get_ingredient(ingredient_internal_id=5, include_inactive=True)

    assert response == {"presented": {"id": 5}}
    assert controller.read_use_case.calls[-1][1]["include_inactive"] is True


def test_get_ingredient_not_found(controller):
    controller.read_use_case = StubUseCase(
        exception=IngredientNotFoundException("missing")
    )

    with pytest.raises(HTTPException) as captured:
        controller.get_ingredient(ingredient_internal_id=99)

    assert captured.value.status_code == HTTPStatus.NOT_FOUND
    assert captured.value.detail["error"] == "missing"


def test_update_ingredient_success(controller):
    controller.update_use_case = StubUseCase(result={"id": 2, "name": "Updated"})

    response = controller.update_ingredient(
        {
            "internal_id": 2,
            "name": "Updated",
            "price": 2.5,
            "ingredient_type": IngredientType.MEAT,
        }
    )

    assert response["presented"]["id"] == 2
    assert response["presented"]["name"] == "Updated"


def test_update_ingredient_not_found(controller):
    controller.update_use_case = StubUseCase(
        exception=IngredientNotFoundException("gone")
    )

    with pytest.raises(HTTPException) as captured:
        controller.update_ingredient({"internal_id": 7})

    assert captured.value.status_code == HTTPStatus.NOT_FOUND
    assert captured.value.detail["error"] == "gone"


def test_update_ingredient_bad_request(controller):
    controller.update_use_case = StubUseCase(
        exception=IngredientAlreadyExistsException("exists")
    )

    with pytest.raises(HTTPException) as captured:
        controller.update_ingredient({"internal_id": 8})

    assert captured.value.status_code == HTTPStatus.BAD_REQUEST
    assert captured.value.detail["error"] == "exists"


def test_delete_ingredient_success(controller):
    controller.delete_use_case = StubUseCase(result=True)

    response = controller.delete_ingredient(ingredient_internal_id=3)

    assert response["presented"]["success"] is True
    assert "soft deleted" in response["presented"]["message"]


def test_delete_ingredient_not_found(controller):
    controller.delete_use_case = StubUseCase(
        exception=IngredientNotFoundException("not found")
    )

    with pytest.raises(HTTPException) as captured:
        controller.delete_ingredient(ingredient_internal_id=11)

    assert captured.value.status_code == HTTPStatus.NOT_FOUND
    assert captured.value.detail["error"] == "not found"


def test_list_ingredients_success(controller):
    controller.list_use_case = StubUseCase(result=[{"id": 1}, {"id": 2}])

    response = controller.list_ingredients(include_inactive=False)

    assert response["presented"] == [{"id": 1}, {"id": 2}]


def test_list_ingredients_internal_error(controller):
    controller.list_use_case = StubUseCase(exception=RuntimeError("fail"))

    with pytest.raises(HTTPException) as captured:
        controller.list_ingredients()

    assert captured.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert captured.value.detail["error"] == "fail"


def test_list_ingredients_by_type_success(controller):
    controller.list_by_type_use_case = StubUseCase(result=[{"id": 5}])

    response = controller.list_ingredients_by_type(IngredientType.SAUCE, include_inactive=True)

    assert response["presented"] == [{"id": 5}]
    assert controller.list_by_type_use_case.calls[-1][0][0] == IngredientType.SAUCE


def test_list_ingredients_by_type_not_found(controller):
    controller.list_by_type_use_case = StubUseCase(
        exception=IngredientNotFoundException("none")
    )

    with pytest.raises(HTTPException) as captured:
        controller.list_ingredients_by_type(IngredientType.SALAD)

    assert captured.value.status_code == HTTPStatus.NOT_FOUND
    assert captured.value.detail["error"] == "none"


def test_list_ingredients_by_applies_to_success(controller):
    controller.list_by_applies_to_use_case = StubUseCase(result=[{"id": 9}])

    response = controller.list_ingredients_by_applies_to(ProductCategory.DRINK)

    assert response["presented"] == [{"id": 9}]
    assert controller.list_by_applies_to_use_case.calls[-1][0][0] == ProductCategory.DRINK


def test_list_ingredients_by_applies_to_not_found(controller):
    controller.list_by_applies_to_use_case = StubUseCase(
        exception=IngredientNotFoundException("empty")
    )

    with pytest.raises(HTTPException) as captured:
        controller.list_ingredients_by_applies_to(ProductCategory.BURGER, include_inactive=True)

    assert captured.value.status_code == HTTPStatus.NOT_FOUND
    assert captured.value.detail["error"] == "empty"
    assert controller.list_by_applies_to_use_case.calls[-1][1]["include_inactive"] is True


def test_list_ingredient_types_success(controller):
    result = controller.list_ingredient_types()

    assert result["total_count"] == len(IngredientType)
    assert {"value": IngredientType.BREAD.value, "name": IngredientType.BREAD.name} in result["ingredient_types"]


def test_list_ingredient_types_error(controller, monkeypatch):
    class BadEnum:
        def __iter__(self):
            raise RuntimeError("enum broke")

    monkeypatch.setattr(ingredient_controller_module, "IngredientType", BadEnum())

    with pytest.raises(HTTPException) as captured:
        controller.list_ingredient_types()

    assert captured.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert captured.value.detail["error"] == "enum broke"
