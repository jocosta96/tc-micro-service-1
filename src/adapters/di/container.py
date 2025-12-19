from src.application.repositories.customer_repository import CustomerRepository
from src.application.repositories.ingredient_repository import IngredientRepository
from src.application.repositories.product_repository import ProductRepository
from src.adapters.gateways.sql_customer_repository import SQLCustomerRepository
from src.adapters.gateways.sql_ingredient_repository import SQLIngredientRepository
from src.adapters.gateways.sql_product_repository import SQLProductRepository
from src.adapters.gateways.implementations.sqlalchemy_database import SQLAlchemyDatabase
from src.adapters.gateways.interfaces.database_interface import DatabaseInterface
from src.adapters.presenters.implementations.json_presenter import JSONPresenter
from src.adapters.presenters.interfaces.presenter_interface import PresenterInterface


class Container:
    """
    Dependency Injection Container.

    In Clean Architecture:
    - This wires up all the components
    - It's part of the Frameworks & Drivers layer
    - It creates the concrete implementations
    - It manages the dependency graph
    """

    def __init__(self, database_url: str = None):
        self.database_url = database_url
        self._database: DatabaseInterface = None
        self._customer_repository: CustomerRepository = None
        self._ingredient_repository: IngredientRepository = None
        self._product_repository: ProductRepository = None
        self._qr_payment_repository = None
        self._presenter: PresenterInterface = None

    @property
    def database(self) -> DatabaseInterface:
        """Get database instance"""
        if self._database is None:
            self._database = SQLAlchemyDatabase(self.database_url)
        return self._database

    @property
    def customer_repository(self) -> CustomerRepository:
        """Get customer repository instance"""
        if self._customer_repository is None:
            self._customer_repository = SQLCustomerRepository(self.database)
        return self._customer_repository

    @property
    def ingredient_repository(self) -> IngredientRepository:
        """Get ingredient repository instance"""
        if self._ingredient_repository is None:
            self._ingredient_repository = SQLIngredientRepository(self.database)
        return self._ingredient_repository

    @property
    def product_repository(self) -> ProductRepository:
        """Get product repository instance"""
        if self._product_repository is None:
            self._product_repository = SQLProductRepository(self.database, self.ingredient_repository)
        return self._product_repository

    @property
    def presenter(self) -> PresenterInterface:
        """Get presenter instance"""
        if self._presenter is None:
            self._presenter = JSONPresenter()
        return self._presenter

    def reset(self):
        """Reset all dependencies (useful for testing)"""
        self._database = None
        self._customer_repository = None
        self._ingredient_repository = None
        self._product_repository = None
        self._presenter = None


# Global container instance
container = Container()
