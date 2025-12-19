from src.entities.ingredient import Ingredient, IngredientType
from src.application.repositories.ingredient_repository import IngredientRepository
from src.application.dto import (
    IngredientCreateRequest,
    IngredientUpdateRequest,
    IngredientResponse,
    IngredientListResponse,
)
from src.application.exceptions import (
    IngredientNotFoundException,
    IngredientAlreadyExistsException
)
from src.app_logs import get_logger
from src.entities.value_objects.money import Money
from decimal import Decimal
from src.entities.product import ProductCategory



class IngredientCreateUseCase:
    """Use case for creating a new ingredient"""

    def __init__(self, ingredient_repository: IngredientRepository):
        self.ingredient_repository = ingredient_repository
        self.logger = get_logger("IngredientCreateUseCase")

    def execute(self, request: IngredientCreateRequest) -> IngredientResponse:
        """Execute the create ingredient use case"""
        self.logger.info(
            "Creating new ingredient", name=request.name, type=request.type
        )

        ingredient = Ingredient.create(
            name=request.name,
            price=Money(amount=Decimal(str(request.price))),
            is_active=request.is_active,
            type=request.type,
            applies_to_burger=request.applies_to_burger,
            applies_to_side=request.applies_to_side,
            applies_to_drink=request.applies_to_drink,
            applies_to_dessert=request.applies_to_dessert,
        )

        if self.ingredient_repository.exists_by_name(ingredient.name.value):
            self.logger.warning(
                "Ingredient creation failed - name already exists",
                name=ingredient.name.value,
            )
            raise IngredientAlreadyExistsException(
                f"Ingredient with name {ingredient.name.value} already exists"
            )

        saved_ingredient = self.ingredient_repository.save(ingredient)

        self.logger.info(
            "Ingredient created successfully",
            ingredient_id=saved_ingredient.internal_id,
            name=saved_ingredient.name.value,
        )

        return IngredientResponse.from_entity(saved_ingredient)


class IngredientReadUseCase:
    """Use case for reading a ingredient"""

    def __init__(self, ingredient_repository: IngredientRepository):
        self.ingredient_repository = ingredient_repository
        self.logger = get_logger("IngredientReadUseCase")

    def execute(self, ingredient_internal_id: int, include_inactive: bool = False) -> IngredientResponse:
        """Execute the read ingredient use case"""
        ingredient = self.ingredient_repository.find_by_id(ingredient_internal_id, include_inactive=include_inactive)
        if not ingredient:
            raise IngredientNotFoundException(
                f"Ingredient with internal_id {ingredient_internal_id} not found"
            )
        return IngredientResponse.from_entity(ingredient)


class IngredientUpdateUseCase:
    """Use case for updating a ingredient"""

    def __init__(self, ingredient_repository: IngredientRepository):
        self.ingredient_repository = ingredient_repository
        self.logger = get_logger("IngredientUpdateUseCase")

    def execute(self, request: IngredientUpdateRequest) -> IngredientResponse:
        """Execute the update ingredient use case"""
        self.logger.info(
            "Updating ingredient",
            ingredient_id=request.internal_id,
            name=request.name,
            type=request.type,
        )

        ingredient = Ingredient.create(
            name=request.name,
            price=Money(amount=Decimal(str(request.price))),
            is_active=request.is_active,
            type=request.type,
            applies_to_burger=request.applies_to_burger,
            applies_to_side=request.applies_to_side,
            applies_to_drink=request.applies_to_drink,
            applies_to_dessert=request.applies_to_dessert,
            internal_id=request.internal_id,
        )

        existing_ingredient = self.ingredient_repository.find_by_id(ingredient.internal_id, include_inactive=True)
        if not existing_ingredient:
            raise IngredientNotFoundException(
                f"Ingredient with internal_id {ingredient.internal_id} not found"
            )

        if existing_ingredient.name.value != ingredient.name.value:
            if self.ingredient_repository.exists_by_name(ingredient.name.value, include_inactive=True):
                raise IngredientAlreadyExistsException(
                    f"Ingredient with name {ingredient.name.value} already exists"
                )

        saved_ingredient = self.ingredient_repository.save(ingredient)

        self.logger.info(
            "Ingredient updated successfully",
            ingredient_id=saved_ingredient.internal_id,
            name=saved_ingredient.name.value,
        )
        return IngredientResponse.from_entity(saved_ingredient)


class IngredientDeleteUseCase:
    """Use case for deleting a ingredient"""

    def __init__(self, ingredient_repository: IngredientRepository):
        self.ingredient_repository = ingredient_repository
        self.logger = get_logger("IngredientDeleteUseCase")

    def execute(self, ingredient_internal_id: int) -> bool:
        """Execute the delete ingredient use case"""

        existing_ingredient = self.ingredient_repository.find_by_id(ingredient_internal_id, include_inactive=True)
        if not existing_ingredient:
            raise IngredientNotFoundException(
                f"Ingredient with internal_id {ingredient_internal_id} not found"
            )

        # Soft delete the ingredient
        return self.ingredient_repository.delete(ingredient_internal_id)


class IngredientListUseCase:
    """Use case for listing ingredients"""

    def __init__(self, ingredient_repository: IngredientRepository):
        self.ingredient_repository = ingredient_repository
        self.logger = get_logger("IngredientListUseCase")

    def execute(self, include_inactive: bool = False) -> IngredientListResponse:
        """Execute the list ingredients use case"""
        ingredients = self.ingredient_repository.find_all(include_inactive=include_inactive)
        ingredient_responses = [
            IngredientResponse.from_entity(ingredient) for ingredient in ingredients
        ]
        return IngredientListResponse(
            ingredients=ingredient_responses, total_count=len(ingredient_responses)
        )

class IngredientListByTypeUseCase:
    """Use case for getting a ingredient by type"""

    def __init__(self, ingredient_repository: IngredientRepository):
        self.ingredient_repository = ingredient_repository
        self.logger = get_logger("IngredientListByTypeUseCase")

    def execute(self, type: IngredientType, include_inactive: bool = False) -> IngredientListResponse:
        """Execute the get ingredient by type use case"""
        ingredients = self.ingredient_repository.find_by_type(type, include_inactive=include_inactive)
        ingredient_responses = [
            IngredientResponse.from_entity(ingredient) for ingredient in ingredients
        ]
        return IngredientListResponse(
            ingredients=ingredient_responses, total_count=len(ingredient_responses)
        )

class IngredientListByAppliesToUseCase:
    """Use case for getting a ingredient by applies to"""

    def __init__(self, ingredient_repository: IngredientRepository):
        self.ingredient_repository = ingredient_repository
        self.logger = get_logger("IngredientListByAppliesToUseCase")

    def execute(self, category: ProductCategory, include_inactive: bool = False) -> IngredientListResponse:
        """Execute the get ingredient by applies to use case"""
        ingredients = self.ingredient_repository.find_by_applies_usage(
            category, include_inactive=include_inactive
        )
        ingredient_responses = [
            IngredientResponse.from_entity(ingredient) for ingredient in ingredients
        ]
        return IngredientListResponse(
            ingredients=ingredient_responses, total_count=len(ingredient_responses)
        )