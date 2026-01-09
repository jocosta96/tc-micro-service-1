from fastapi import APIRouter, Depends
from typing_extensions import Annotated
from pydantic import BaseModel
from typing import Optional


from src.adapters.controllers.customer_controller import CustomerController


# Pydantic models for request/response validation
class CustomerCreateModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    document: str


class CustomerUpdateModel(BaseModel):
    internal_id: int
    first_name: str
    last_name: str
    email: str
    document: str


class CustomerResponseModel(BaseModel):
    internal_id: Optional[int]
    first_name: str
    last_name: str
    email: str
    document: str
    full_name: str
    is_anonymous: bool
    is_registered: bool
    is_active: bool
    created_at: Optional[str]


class CustomerListResponseModel(BaseModel):
    data: list[CustomerResponseModel]
    total_count: int
    timestamp: str





# Dependency injection function
def get_customer_controller() -> CustomerController:
    """Dependency injection for customer controller"""
    from src.adapters.di.container import container
    from src.adapters.presenters.implementations.json_presenter import JSONPresenter

    return CustomerController(container.customer_repository, JSONPresenter())


# Create router
customer_router = APIRouter(tags=["customer"], prefix="/customer")


@customer_router.get("/anonymous", response_model=CustomerResponseModel)
def get_anonymous_customer(
    controller: Annotated[CustomerController, Depends(get_customer_controller)]
):
    """Get anonymous customer endpoint"""
    return controller.get_anonymous_customer()


@customer_router.get("/list", response_model=CustomerListResponseModel)
def list_customers(
    controller: Annotated[CustomerController, Depends(get_customer_controller)],
    include_inactive: bool = False,
):
    """List all customers endpoint"""
    return controller.list_customers(include_inactive=include_inactive)


@customer_router.get("/by-id/{customer_id}", response_model=CustomerResponseModel)
def get_customer(
    customer_id: int,
    controller: Annotated[CustomerController, Depends(get_customer_controller)],
    include_inactive: bool = False,
):
    """Get customer by ID endpoint"""
    return controller.get_customer(customer_id, include_inactive=include_inactive)


@customer_router.post("/create", response_model=CustomerResponseModel)
def create_customer(
    customer_data: CustomerCreateModel,
    controller: Annotated[CustomerController, Depends(get_customer_controller)],
):
    """Create customer endpoint"""
    return controller.create_customer(customer_data.dict())


@customer_router.put("/update", response_model=CustomerResponseModel)
def update_customer(
    customer_data: CustomerUpdateModel,
    controller: Annotated[CustomerController, Depends(get_customer_controller)],
):
    """Update customer endpoint"""
    return controller.update_customer(customer_data.dict())


@customer_router.delete("/delete/{customer_id}")
def delete_customer(
    customer_id: int,
    controller: Annotated[CustomerController, Depends(get_customer_controller)],
):
    """Delete customer endpoint"""
    return controller.delete_customer(customer_id)
