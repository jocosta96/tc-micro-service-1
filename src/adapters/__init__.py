# Interface Adapters Layer
# This layer handles external concerns like HTTP, databases, and data formatting

from .routes.customer_routes import customer_router
from .routes.health_routes import health_router
from .controllers.customer_controller import CustomerController
from .gateways.sql_customer_repository import SQLCustomerRepository
from .di.container import Container, container
from .presenters.implementations.json_presenter import JSONPresenter

__all__ = [
    "customer_router",
    "health_router",
    "CustomerController",
    "SQLCustomerRepository",
    "Container",
    "container",
    "JSONPresenter",
]
