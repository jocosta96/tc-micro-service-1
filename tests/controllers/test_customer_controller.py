from http import HTTPStatus
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from src.adapters.controllers.customer_controller import CustomerController
from src.adapters.presenters.interfaces.presenter_interface import PresenterInterface
from src.application.exceptions import (
    CustomerAlreadyExistsException,
    CustomerBusinessRuleException,
    CustomerNotFoundException,
    CustomerValidationException,
)


class FakePresenter(PresenterInterface):
    def __init__(self):
        self.presented = []
        self.errors = []

    def present(self, data):
        self.presented.append(data)
        return {"presented": data}

    def present_list(self, data_list):
        self.presented.append(data_list)
        return {"presented_list": data_list}

    def present_error(self, error: Exception) -> dict:
        self.errors.append(error)
        return {"error": str(error)}


class StubUseCase:
    def __init__(self, result=None, exception: Exception | None = None):
        self.result = result
        self.exception = exception

    def execute(self, *args, **kwargs):
        if self.exception:
            raise self.exception
        return self.result


@pytest.fixture
def presenter():
    return FakePresenter()


@pytest.fixture
def controller(presenter):
    class Repo:
        """Minimal repository placeholder for controller wiring."""

    return CustomerController(Repo(), presenter)


def test_get_anonymous_customer_success(controller):
    controller.anonymous_use_case = StubUseCase(result={"id": "anon"})

    response = controller.get_anonymous_customer()

    assert response == {"presented": {"id": "anon"}}


def test_get_anonymous_customer_not_found(controller):
    controller.anonymous_use_case = StubUseCase(
        exception=CustomerNotFoundException("missing")
    )

    with pytest.raises(HTTPException) as exc:
        controller.get_anonymous_customer()

    assert exc.value.status_code == HTTPStatus.NOT_FOUND
    assert exc.value.detail["error"] == "missing"


def test_get_anonymous_customer_business_rule_error(controller):
    controller.anonymous_use_case = StubUseCase(
        exception=CustomerBusinessRuleException("rule broken")
    )

    with pytest.raises(HTTPException) as exc:
        controller.get_anonymous_customer()

    assert exc.value.status_code == HTTPStatus.BAD_REQUEST
    assert exc.value.detail["error"] == "rule broken"


def test_get_customer_success(controller):
    controller.read_use_case = StubUseCase(result=SimpleNamespace(internal_id=1))

    response = controller.get_customer(customer_internal_id=1)

    assert response["presented"].internal_id == 1


def test_get_customer_not_found(controller):
    controller.read_use_case = StubUseCase(
        exception=CustomerNotFoundException("not here")
    )

    with pytest.raises(HTTPException) as exc:
        controller.get_customer(customer_internal_id=42)

    assert exc.value.status_code == HTTPStatus.NOT_FOUND
    assert exc.value.detail["error"] == "not here"


def test_get_customer_unexpected_error(controller):
    controller.read_use_case = StubUseCase(exception=RuntimeError("boom"))

    with pytest.raises(HTTPException) as exc:
        controller.get_customer(customer_internal_id=5)

    assert exc.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert exc.value.detail["error"] == "boom"


def test_create_customer_success(controller):
    controller.create_use_case = StubUseCase(result={"id": 10})

    response = controller.create_customer(
        {
            "first_name": "A",
            "last_name": "B",
            "email": "a@b.com",
            "document": "123",
        }
    )

    assert response == {"presented": {"id": 10}}


def test_create_customer_bad_request(controller):
    controller.create_use_case = StubUseCase(
        exception=CustomerAlreadyExistsException("duplicate")
    )

    with pytest.raises(HTTPException) as exc:
        controller.create_customer({})

    assert exc.value.status_code == HTTPStatus.BAD_REQUEST
    assert exc.value.detail["error"] == "duplicate"


def test_update_customer_success(controller):
    controller.update_use_case = StubUseCase(result={"id": 2, "first_name": "New"})

    response = controller.update_customer(
        {
            "internal_id": 2,
            "first_name": "New",
            "last_name": "Name",
            "email": "new@example.com",
            "document": "doc",
        }
    )

    assert response["presented"]["id"] == 2
    assert response["presented"]["first_name"] == "New"


def test_update_customer_validation_error(controller):
    controller.update_use_case = StubUseCase(
        exception=CustomerValidationException("invalid")
    )

    with pytest.raises(HTTPException) as exc:
        controller.update_customer({"internal_id": 5})

    assert exc.value.status_code == HTTPStatus.BAD_REQUEST
    assert exc.value.detail["error"] == "invalid"


def test_list_customers_success(controller):
    controller.list_use_case = StubUseCase(result=[{"id": 1}, {"id": 2}])

    response = controller.list_customers(include_inactive=True)

    assert response["presented"] == [{"id": 1}, {"id": 2}]


def test_list_customers_business_rule_error(controller):
    controller.list_use_case = StubUseCase(
        exception=CustomerBusinessRuleException("blocked")
    )

    with pytest.raises(HTTPException) as exc:
        controller.list_customers()

    assert exc.value.status_code == HTTPStatus.BAD_REQUEST
    assert exc.value.detail["error"] == "blocked"


def test_delete_customer_success(controller):
    controller.delete_use_case = StubUseCase(result=True)

    response = controller.delete_customer(customer_internal_id=9)

    assert response["presented"]["success"] is True
    assert "soft deleted" in response["presented"]["message"]


def test_delete_customer_not_found(controller):
    controller.delete_use_case = StubUseCase(
        exception=CustomerNotFoundException("gone")
    )

    with pytest.raises(HTTPException) as exc:
        controller.delete_customer(customer_internal_id=99)

    assert exc.value.status_code == HTTPStatus.NOT_FOUND
    assert exc.value.detail["error"] == "gone"


def test_delete_customer_unexpected_error(controller):
    controller.delete_use_case = StubUseCase(exception=RuntimeError("kaboom"))

    with pytest.raises(HTTPException) as exc:
        controller.delete_customer(customer_internal_id=7)

    assert exc.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert exc.value.detail["error"] == "kaboom"
