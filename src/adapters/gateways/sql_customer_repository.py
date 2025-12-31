from typing import List, Optional

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

from src.adapters.gateways.shared_base import Base
from src.application.repositories.customer_repository import CustomerRepository
from src.entities.customer import Customer
from src.entities.value_objects.email import Email
from src.entities.value_objects.name import Name
from src.entities.value_objects.document import Document
from src.adapters.gateways.interfaces.database_interface import DatabaseInterface


class CustomerModel(Base):
    """SQLAlchemy model for Customer table"""

    __tablename__ = "customers"

    internal_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True, unique=True)
    document = Column(String(11), nullable=True, unique=True)
    is_anonymous = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


class SQLCustomerRepository(CustomerRepository):
    """
    SQL implementation of CustomerRepository.

    In Clean Architecture:
    - This is part of the Interface Adapters layer (Gateway)
    - It implements the repository interface
    - It uses the database interface for ORM operations
    - It converts between database models and domain entities
    """

    def __init__(self, database: DatabaseInterface):
        self.database = database

    def _get_session(self):
        """Get database session"""
        return self.database.get_session()

    def _to_entity(self, model: CustomerModel) -> Customer:
        """Convert database model to domain entity"""
        # Create customer without triggering validation since data comes from database
        customer = Customer.__new__(Customer)
        customer.first_name = Name.create(model.first_name)
        customer.last_name = Name.create(model.last_name)
        customer.email = Email.create(model.email or "")
        customer.document = Document.create(model.document or "")
        customer.is_active = model.is_active
        customer.is_anonymous = model.is_anonymous
        customer.internal_id = model.internal_id
        customer.created_at = model.created_at
        return customer

    def _to_model(self, customer: Customer) -> CustomerModel:
        """Convert domain entity to database model"""
        return CustomerModel(
            internal_id=customer.internal_id,
            first_name=customer.first_name.value,
            last_name=customer.last_name.value,
            email=customer.email.value if not customer.email.value == "" else None,
            document=customer.document.value
            if not customer.document.is_empty
            else None,
            is_anonymous=customer.is_anonymous,
            is_active=customer.is_active,
            created_at=customer.created_at,
        )

    def save(self, customer: Customer) -> Customer:
        """Save a customer and return the saved customer with ID"""
        session = self._get_session()
        try:
            if customer.internal_id:
                # Try to find existing customer for update
                db_customer = self.database.find_by_field(
                    session, CustomerModel, "internal_id", customer.internal_id
                )
                if db_customer:
                    # Update existing customer
                    db_customer.first_name = customer.first_name.value
                    db_customer.last_name = customer.last_name.value
                    db_customer.email = (
                        customer.email.value if not customer.email.value == "" else None
                    )
                    db_customer.document = (
                        customer.document.value if not customer.document.is_empty else None
                    )
                    db_customer.is_anonymous = customer.is_anonymous
                    db_customer.is_active = customer.is_active
                    # Don't update created_at for existing customers

                    self.database.update(session, db_customer)
                else:
                    # Customer has internal_id but doesn't exist in DB, treat as new customer
                    db_customer = self._to_model(customer)
                    self.database.add(session, db_customer)
            else:
                # Create new customer without internal_id
                db_customer = self._to_model(customer)
                self.database.add(session, db_customer)

            self.database.commit(session)
            return self._to_entity(db_customer)
        except Exception as e:
            self.database.rollback(session)
            raise e
        finally:
            self.database.close_session(session)

    def find_by_id(self, customer_internal_id: int, include_inactive: bool = False) -> Optional[Customer]:
        """Find a customer by ID"""
        session = self._get_session()
        try:
            db_customer = self.database.find_by_field(session, CustomerModel, "internal_id", customer_internal_id)
            if not db_customer:
                return None
            
            # Filter by active status if not including inactive
            if not include_inactive and not db_customer.is_active:
                return None
                
            return self._to_entity(db_customer)
        finally:
            self.database.close_session(session)

    def find_by_document(self, document: str, include_inactive: bool = False) -> Optional[Customer]:
        """Find a customer by document number"""
        session = self._get_session()
        try:
            db_customer = self.database.find_by_field(
                session, CustomerModel, "document", document
            )
            if not db_customer:
                return None
                
            # Filter by active status if not including inactive
            if not include_inactive and not db_customer.is_active:
                return None
                
            return self._to_entity(db_customer)
        finally:
            self.database.close_session(session)

    def find_by_email(self, email: str, include_inactive: bool = False) -> Optional[Customer]:
        """Find a customer by email"""
        session = self._get_session()
        try:
            db_customer = self.database.find_by_field(
                session, CustomerModel, "email", email
            )
            if not db_customer:
                return None
                
            # Filter by active status if not including inactive
            if not include_inactive and not db_customer.is_active:
                return None
                
            return self._to_entity(db_customer)
        finally:
            self.database.close_session(session)

    def find_all(self, include_inactive: bool = False) -> List[Customer]:
        """Find all customers"""
        session = self._get_session()
        try:
            if include_inactive:
                db_customers = self.database.find_all(session, CustomerModel)
            else:
                # Filter only active customers
                db_customers = self.database.find_all_by_field(session, CustomerModel, "is_active", True)
            return [self._to_entity(customer) for customer in db_customers]
        finally:
            self.database.close_session(session)

    def delete(self, customer_internal_id: int) -> bool:
        """Soft delete a customer by ID using the entity's business rule, return True if deleted"""
        session = self._get_session()
        try:
            db_customer = self.database.find_by_field(session, CustomerModel, "internal_id", customer_internal_id)
            if not db_customer:
                return False

            # Convert to entity and apply business rule
            customer_entity = self._to_entity(db_customer)
            customer_entity.soft_delete()
            
            # Update the database model with the entity's changes
            db_customer.is_active = customer_entity.is_active
            db_customer.first_name = customer_entity.first_name.value
            db_customer.last_name = customer_entity.last_name.value
            db_customer.email = customer_entity.email.value
            db_customer.document = customer_entity.document.value
            db_customer.is_anonymous = customer_entity.is_anonymous
            
            self.database.update(session, db_customer)
            self.database.commit(session)
            return True
        except Exception as e:
            self.database.rollback(session)
            raise e
        finally:
            self.database.close_session(session)

    def get_anonymous_customer(self) -> Customer:
        """Get or create the anonymous customer"""
        session = self._get_session()
        try:
            # Try to find existing anonymous customer
            db_customer = self.database.find_by_field(
                session, CustomerModel, "is_anonymous", True
            )

            if not db_customer:
                # Create anonymous customer if it doesn't exist
                anonymous_customer = Customer.create_anonymous()
                db_customer = self._to_model(anonymous_customer)
                self.database.add(session, db_customer)
                self.database.commit(session)

            return self._to_entity(db_customer)
        except Exception as e:
            self.database.rollback(session)
            raise e
        finally:
            self.database.close_session(session)

    def exists_by_document(self, document: str, include_inactive: bool = False) -> bool:
        """Check if a customer exists with the given document"""
        session = self._get_session()
        try:
            db_customer = self.database.find_by_field(
                session, CustomerModel, "document", document
            )
            if not db_customer:
                return False
                
            # Check active status if not including inactive
            if not include_inactive and not db_customer.is_active:
                return False
                
            return True
        finally:
            self.database.close_session(session)

    def exists_by_email(self, email: str, include_inactive: bool = False) -> bool:
        """Check if a customer exists with the given email"""
        session = self._get_session()
        try:
            db_customer = self.database.find_by_field(session, CustomerModel, "email", email)
            if not db_customer:
                return False
                
            # Check active status if not including inactive
            if not include_inactive and not db_customer.is_active:
                return False
                
            return True
        finally:
            self.database.close_session(session)
