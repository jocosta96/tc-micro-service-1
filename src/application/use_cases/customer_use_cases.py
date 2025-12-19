from src.application.repositories.customer_repository import CustomerRepository
from src.application.dto.implementation.customer_dto import CustomerCreateRequest, CustomerUpdateRequest, CustomerListResponse, CustomerResponse
from src.application.exceptions import CustomerNotFoundException, CustomerAlreadyExistsException, CustomerBusinessRuleException
from src.entities.customer import Customer
from src.app_logs import get_logger



class CustomerCreateUseCase:
    """
    Use case for creating a new customer.

    This use case:
    - Contains business logic for customer creation
    - Validates business rules
    - Orchestrates between domain and repository
    - Is independent of infrastructure (uses repository interface)
    """

    def __init__(self, customer_repository: CustomerRepository):
        self.customer_repository = customer_repository
        self.logger = get_logger("CustomerCreateUseCase")

    def execute(self, request: CustomerCreateRequest) -> CustomerResponse:
        """Execute the create customer use case"""
        self.logger.info(
            "Creating new customer", first_name=request.first_name, email=request.email
        )

        # Create customer entity from DTO
        customer = Customer.create_registered(
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            document=request.document,
        )

        # Business rule: Check if customer with same document already exists
        if not customer.document.is_empty:
            if self.customer_repository.exists_by_document(customer.document.value):
                self.logger.warning(
                    "Customer creation failed - document already exists",
                    document=customer.document.value,
                )
                raise CustomerAlreadyExistsException(
                    f"Customer with document {customer.document.value} already exists"
                )

        # Business rule: Check if customer with same email already exists
        if not customer.email.value == "":
            if self.customer_repository.exists_by_email(customer.email.value):
                self.logger.warning(
                    "Customer creation failed - email already exists",
                    email=customer.email.value,
                )
                raise CustomerAlreadyExistsException(
                    f"Customer with email {customer.email.value} already exists"
                )

        # Business rule: Customer must be able to place orders
        if not customer.can_place_order():
            self.logger.warning("Customer creation failed - business rules not met")
            raise CustomerBusinessRuleException(
                "Customer does not meet requirements to place orders"
            )

        # Save the customer
        saved_customer = self.customer_repository.save(customer)

        self.logger.info(
            "Customer created successfully",
            customer_id=saved_customer.internal_id,
            full_name=saved_customer.full_name,
        )

        # Return DTO
        return CustomerResponse.from_entity(saved_customer)


class CustomerReadUseCase:
    """Use case for reading customer information"""

    def __init__(self, customer_repository: CustomerRepository):
        self.customer_repository = customer_repository

    def execute(self, customer_internal_id: int, include_inactive: bool = False) -> CustomerResponse:
        """Execute the read customer use case"""
        customer = self.customer_repository.find_by_id(customer_internal_id, include_inactive=include_inactive)
        if not customer:
            raise CustomerNotFoundException(f"Customer with internal_id {customer_internal_id} not found")
        return CustomerResponse.from_entity(customer)


class CustomerUpdateUseCase:
    """Use case for updating customer information"""

    def __init__(self, customer_repository: CustomerRepository):
        self.customer_repository = customer_repository

    def execute(self, request: CustomerUpdateRequest) -> CustomerResponse:
        """Execute the update customer use case"""
        # Create customer entity from DTO
        customer = Customer.create_registered(
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            document=request.document,
            internal_id=request.internal_id,
        )

        # Business rule: Customer must exist
        existing_customer = self.customer_repository.find_by_id(customer.internal_id, include_inactive=True)
        if not existing_customer:
            raise CustomerNotFoundException(f"Customer with internal_id {customer.internal_id} not found")

        # Business rule: Check if new document conflicts with existing customer
        if not customer.document.is_empty:
            existing_by_doc = self.customer_repository.find_by_document(
                customer.document.value, include_inactive=True
            )
            if existing_by_doc and existing_by_doc.internal_id != customer.internal_id:
                raise CustomerAlreadyExistsException(
                    f"Document {customer.document.value} is already used by another customer"
                )

        # Business rule: Check if new email conflicts with existing customer
        if not customer.email.value == "":
            existing_by_email = self.customer_repository.find_by_email(
                customer.email.value, include_inactive=True
            )
            if existing_by_email and existing_by_email.internal_id != customer.internal_id:
                raise CustomerAlreadyExistsException(
                    f"Email {customer.email.value} is already used by another customer"
                )

        # Business rule: Customer must be able to place orders
        if not customer.can_place_order():
            raise CustomerBusinessRuleException(
                "Customer does not meet requirements to place orders"
            )

        # Save the updated customer
        saved_customer = self.customer_repository.save(customer)

        # Return DTO
        return CustomerResponse.from_entity(saved_customer)


class CustomerDeleteUseCase:
    """Use case for deleting a customer"""

    def __init__(self, customer_repository: CustomerRepository):
        self.customer_repository = customer_repository

    def execute(self, customer_internal_id: int) -> bool:
        """Execute the delete customer use case"""
        # Use the repository's dedicated delete method which handles soft deletion properly
        # This method avoids validation issues by updating the database directly
        success = self.customer_repository.delete(customer_internal_id)
        
        if not success:
            raise CustomerNotFoundException(f"Customer with internal_id {customer_internal_id} not found")
        
        return True


class CustomerListUseCase:
    """Use case for listing customers"""

    def __init__(self, customer_repository: CustomerRepository):
        self.customer_repository = customer_repository

    def execute(self, include_inactive: bool = False) -> CustomerListResponse:
        """Execute the list customers use case"""
        customers = self.customer_repository.find_all(include_inactive=include_inactive)
        customer_responses = [
            CustomerResponse.from_entity(customer) for customer in customers
        ]
        return CustomerListResponse(
            customers=customer_responses, total_count=len(customer_responses)
        )


class CustomerGetAnonymousUseCase:
    """Use case for getting the anonymous customer"""

    def __init__(self, customer_repository: CustomerRepository):
        self.customer_repository = customer_repository

    def execute(self) -> CustomerResponse:
        """Execute the get anonymous customer use case"""
        customer = self.customer_repository.get_anonymous_customer()
        return CustomerResponse.from_entity(customer)
