from typing import List, Optional

from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, DateTime
from src.adapters.gateways.shared_base import Base
from src.application.repositories.ingredient_repository import IngredientRepository
from src.entities.ingredient import Ingredient, IngredientType
from src.adapters.gateways.interfaces.database_interface import DatabaseInterface
from src.entities.value_objects.name import Name
from src.entities.value_objects.money import Money
from datetime import datetime
from src.entities.product import ProductCategory


class IngredientModel(Base):
    """SQLAlchemy model for Ingredient table"""

    __tablename__ = "ingredients"

    internal_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    type = Column(String(100), nullable=False)
    applies_to_burger = Column(Boolean, default=False)
    applies_to_side = Column(Boolean, default=False)
    applies_to_drink = Column(Boolean, default=False)
    applies_to_dessert = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)


class SQLIngredientRepository(IngredientRepository):
    """
    SQL implementation of IngredientRepository.

    In Clean Architecture:
    - This is part of the Interface Adapters layer (Gateway)
    - It implements the repository interface
    - It uses the database interface for ORM operations
    - It converts between database models and domain entities
    """

    def __init__(self, database: DatabaseInterface):
        self.database = database

    def _get_session(self):
        """Get a SQLAlchemy session"""
        return self.database.get_session()

    def _to_entity(self, model: IngredientModel) -> Ingredient:
        """Convert a database model to an entity"""
        return Ingredient(
            internal_id=model.internal_id,
            name=Name.create(model.name),
            price=Money(amount=model.price),
            is_active=model.is_active,
            type=IngredientType(model.type),
            applies_to_burger=model.applies_to_burger,
            applies_to_side=model.applies_to_side,
            applies_to_drink=model.applies_to_drink,
            applies_to_dessert=model.applies_to_dessert,
        )

    def _to_model(self, ingredient: Ingredient) -> IngredientModel:
        """Convert an entity to a database model"""
        return IngredientModel(
            internal_id=ingredient.internal_id,
            name=ingredient.name.value,
            price=ingredient.price.amount,
            is_active=ingredient.is_active,
            type=ingredient.type.value,
            applies_to_burger=ingredient.applies_to_burger,
            applies_to_side=ingredient.applies_to_side,
            applies_to_drink=ingredient.applies_to_drink,
            applies_to_dessert=ingredient.applies_to_dessert,
        )

    def save(self, ingredient: Ingredient) -> Ingredient:
        """Save an ingredient and return the saved ingredient with ID"""
        session = self._get_session()
        try:
            if ingredient.internal_id:
                # Try to find existing ingredient for update
                db_ingredient = self.database.find_by_field(
                    session, IngredientModel, "internal_id", ingredient.internal_id
                )
                if db_ingredient:
                    # Update existing ingredient
                    db_ingredient.name = ingredient.name.value
                    db_ingredient.price = ingredient.price.amount
                    db_ingredient.is_active = ingredient.is_active
                    db_ingredient.type = ingredient.type.value
                    db_ingredient.applies_to_burger = ingredient.applies_to_burger
                    db_ingredient.applies_to_side = ingredient.applies_to_side
                    db_ingredient.applies_to_drink = ingredient.applies_to_drink
                    db_ingredient.applies_to_dessert = ingredient.applies_to_dessert

                    self.database.update(session, db_ingredient)
                else:
                    # Ingredient has internal_id but doesn't exist in DB, treat as new ingredient
                    db_ingredient = self._to_model(ingredient)
                    self.database.add(session, db_ingredient)
            else:
                # Create new ingredient without internal_id
                db_ingredient = self._to_model(ingredient)
                self.database.add(session, db_ingredient)

            self.database.commit(session)
            return self._to_entity(db_ingredient)
        except Exception as e:
            self.database.rollback(session)
            raise e
        finally:
            self.database.close_session(session)

    def find_by_id(self, ingredient_internal_id: int, include_inactive: bool = False) -> Optional[Ingredient]:
        """Find an ingredient by ID"""
        session = self._get_session()
        try:
            db_ingredient = self.database.find_by_field(session, IngredientModel, "internal_id", ingredient_internal_id)
            if not db_ingredient:
                return None
                
            # Filter by active status if not including inactive
            if not include_inactive and not db_ingredient.is_active:
                return None
                
            return self._to_entity(db_ingredient)
        finally:
            self.database.close_session(session)

    def find_by_name(self, name: str, include_inactive: bool = False) -> Optional[Ingredient]:
        """Find an ingredient by name"""
        session = self._get_session()
        try:
            db_ingredient = self.database.find_by_field(session, IngredientModel, "name", name)
            if not db_ingredient:
                return None
                
            # Filter by active status if not including inactive
            if not include_inactive and not db_ingredient.is_active:
                return None
                
            return self._to_entity(db_ingredient)
        finally:
            self.database.close_session(session)

    def find_by_type(self, type: IngredientType, include_inactive: bool = False) -> List[Ingredient]:
        """Find ingredients by type"""
        session = self._get_session()
        try:
            db_ingredients = self.database.find_all_by_field(session, IngredientModel, "type", type.value)
            ingredients = [self._to_entity(db_ingredient) for db_ingredient in db_ingredients]
            
            # Filter by active status if not including inactive
            if not include_inactive:
                ingredients = [ingredient for ingredient in ingredients if ingredient.is_active]
                
            return ingredients
        finally:
            self.database.close_session(session)

    def find_by_applies_usage(
        self,
        category: ProductCategory,
        include_inactive: bool = False
    ) -> List[Ingredient]:
        """Find ingredients by applies to usage"""
        session = self._get_session()
        try:
            # Initialize all applies_to fields to False
            applies_to_burger = False
            applies_to_side = False
            applies_to_drink = False
            applies_to_dessert = False

            # Set the appropriate field to True based on category
            if category == ProductCategory.BURGER:
                applies_to_burger = True
            elif category == ProductCategory.SIDE:
                applies_to_side = True
            elif category == ProductCategory.DRINK:
                applies_to_drink = True
            elif category == ProductCategory.DESSERT:
                applies_to_dessert = True

            field_values = {
                "applies_to_burger": applies_to_burger,
                "applies_to_side": applies_to_side,
                "applies_to_drink": applies_to_drink,
                "applies_to_dessert": applies_to_dessert,
            }
            db_ingredients = self.database.find_all_by_multiple_fields(session, IngredientModel, field_values)
            ingredients = [self._to_entity(db_ingredient) for db_ingredient in db_ingredients]
            
            # Filter by active status if not including inactive
            if not include_inactive:
                ingredients = [ingredient for ingredient in ingredients if ingredient.is_active]
                
            return ingredients
        finally:
            self.database.close_session(session)

    def find_all(self, include_inactive: bool = False) -> List[Ingredient]:
        """Find all ingredients"""
        session = self._get_session()
        try:
            if include_inactive:
                db_ingredients = self.database.find_all(session, IngredientModel)
            else:
                # Filter only active ingredients
                db_ingredients = self.database.find_all_by_boolean_field(session, IngredientModel, "is_active", True)
            return [self._to_entity(db_ingredient) for db_ingredient in db_ingredients]
        finally:
            self.database.close_session(session)

    def delete(self, ingredient_internal_id: int) -> bool:
        """Soft delete an ingredient by ID (set is_active to False), return True if deleted"""
        session = self._get_session()
        try:
            db_ingredient = self.database.find_by_field(session, IngredientModel, "internal_id", ingredient_internal_id)
            if not db_ingredient:
                return False

            # Soft delete - set is_active to False
            db_ingredient.is_active = False
            self.database.update(session, db_ingredient)
            self.database.commit(session)
            return True
        except Exception as e:
            self.database.rollback(session)
            raise e
        finally:
            self.database.close_session(session)

    def exists_by_name(self, name: str, include_inactive: bool = False) -> bool:
        """Check if an ingredient exists with the given name"""
        session = self._get_session()
        try:
            db_ingredient = self.database.find_by_field(session, IngredientModel, "name", name)
            if not db_ingredient:
                return False
                
            # Check active status if not including inactive
            if not include_inactive and not db_ingredient.is_active:
                return False
                
            return True
        finally:
            self.database.close_session(session)

    def exists_by_type(self, type: IngredientType, include_inactive: bool = False) -> bool:
        """Check if an ingredient exists with the given type"""
        session = self._get_session()
        try:
            db_ingredients = self.database.find_all_by_field(session, IngredientModel, "type", type.value)
            if not db_ingredients:
                return False
                
            # Check if any ingredient of this type is active (if not including inactive)
            if not include_inactive:
                return any(ingredient.is_active for ingredient in db_ingredients)
                
            return True
        finally:
            self.database.close_session(session)