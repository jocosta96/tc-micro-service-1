from fastapi import HTTPException
from http import HTTPStatus

import logging

from src.application.use_cases.customer_use_cases import (
    CustomerCreateUseCase,
    CustomerReadUseCase,
    CustomerUpdateUseCase,
    CustomerDeleteUseCase,
    CustomerListUseCase,
    CustomerGetAnonymousUseCase,
)
from src.application.dto import (
    CustomerCreateRequest,
    CustomerUpdateRequest,
)
from src.application.repositories.customer_repository import CustomerRepository
from src.application.exceptions import (
    CustomerNotFoundException,
    CustomerAlreadyExistsException,
    CustomerBusinessRuleException,
    CustomerValidationException
)
from src.adapters.presenters.interfaces.presenter_interface import PresenterInterface


class CustomerController:
    """
    Customer controller that handles HTTP requests.

    In Clean Architecture:
    - This is part of the Interface Adapters layer
    - It handles HTTP-specific concerns
    - It delegates business logic to use cases
    - It converts between HTTP data and application DTOs
    """

    def __init__(
        self, customer_repository: CustomerRepository, presenter: PresenterInterface
    ):
        self.customer_repository = customer_repository
        self.presenter = presenter
        self.create_use_case = CustomerCreateUseCase(customer_repository)
        self.read_use_case = CustomerReadUseCase(customer_repository)
        self.update_use_case = CustomerUpdateUseCase(customer_repository)
        self.delete_use_case = CustomerDeleteUseCase(customer_repository)
        self.list_use_case = CustomerListUseCase(customer_repository)
        self.anonymous_use_case = CustomerGetAnonymousUseCase(customer_repository)
        self.logger = logging.getLogger(__name__)

    def get_anonymous_customer(self) -> dict:
        """Get anonymous customer endpoint"""
        try:
            customer = self.anonymous_use_case.execute()
            return self.presenter.present(customer)
        except CustomerNotFoundException as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_response)
        except CustomerBusinessRuleException as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail=error_response
            )

    def get_customer(self, customer_internal_id: int, include_inactive: bool = False) -> dict:
        """Get customer by ID endpoint"""

        try:
            self.logger.info(f"Attempting to get customer with internal_id: {customer_internal_id}")
            customer = self.read_use_case.execute(customer_internal_id, include_inactive=include_inactive)
            self.logger.info(f"Successfully retrieved customer: {customer.internal_id}")
            return self.presenter.present(customer)
        except CustomerNotFoundException as e:
            self.logger.warning(f"Customer not found with internal_id: {customer_internal_id}")
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_response)
        except Exception as e:
            self.logger.error(f"Unexpected error getting customer {customer_internal_id}: {e}")
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=error_response)

    def create_customer(self, customer_data: dict) -> dict:
        """Create customer endpoint"""
        try:
            request = CustomerCreateRequest(
                first_name=customer_data.get("first_name", ""),
                last_name=customer_data.get("last_name", ""),
                email=customer_data.get("email", ""),
                document=customer_data.get("document", ""),
            )
            customer = self.create_use_case.execute(request)
            return self.presenter.present(customer)
        except (
            CustomerAlreadyExistsException,
            CustomerBusinessRuleException,
            CustomerValidationException,
        ) as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail=error_response
            )

    def update_customer(self, customer_data: dict) -> dict:
        """Update customer endpoint"""

        try:
            request = CustomerUpdateRequest(
                internal_id=customer_data.get("internal_id"),
                first_name=customer_data.get("first_name", ""),
                last_name=customer_data.get("last_name", ""),
                email=customer_data.get("email", ""),
                document=customer_data.get("document", ""),
            )
            customer = self.update_use_case.execute(request)
            return self.presenter.present(customer)
        except (
            CustomerNotFoundException,
            CustomerAlreadyExistsException,
            CustomerBusinessRuleException,
            CustomerValidationException,
        ) as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail=error_response
            )

    def list_customers(self, include_inactive: bool = False) -> dict:
        """List all customers endpoint"""

        try:
            customers = self.list_use_case.execute(include_inactive=include_inactive)
            return self.presenter.present(customers)
        except CustomerBusinessRuleException as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail=error_response
            )

    def delete_customer(self, customer_internal_id: int) -> dict:
        """Delete customer endpoint"""
        try:
            self.logger.info(f"Attempting to delete customer with internal_id: {customer_internal_id}")
            success = self.delete_use_case.execute(customer_internal_id)
            self.logger.info(f"Successfully deleted customer: {customer_internal_id}")
            return self.presenter.present(
                {"success": success, "message": "Customer soft deleted successfully - data replaced with placeholder values"}
            )
        except (CustomerNotFoundException, CustomerBusinessRuleException) as e:
            self.logger.warning(f"Customer deletion failed for internal_id: {customer_internal_id}, error: {e}")
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_response)
        except Exception as e:
            self.logger.error(f"Unexpected error deleting customer {customer_internal_id}: {e}")
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=error_response)
