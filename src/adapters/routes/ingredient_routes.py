from fastapi import APIRouter, Depends
from typing_extensions import Annotated
from pydantic import BaseModel, Field
from typing import Optional

from src.adapters.controllers.ingredient_controller import IngredientController
from src.adapters.di.container import Container
from src.entities.ingredient import IngredientType
from src.adapters.presenters.implementations.json_presenter import JSONPresenter
from src.entities.product import ProductCategory


class IngredientCreateModel(BaseModel):
    name: str
    price: float
    is_active: bool
    ingredient_type: Annotated[IngredientType, Field(alias='type')]
    applies_to_burger: bool
    applies_to_side: bool
    applies_to_drink: bool
    applies_to_dessert: bool

    class Config:
        populate_by_name = True


class IngredientUpdateModel(BaseModel):
    internal_id: int
    name: str
    price: float
    is_active: bool
    ingredient_type: Annotated[IngredientType, Field(alias='type')]
    applies_to_burger: bool
    applies_to_side: bool
    applies_to_drink: bool
    applies_to_dessert: bool

    class Config:
        populate_by_name = True


class IngredientResponseModel(BaseModel):
    model_config = {"populate_by_name": True}
    
    internal_id: Optional[int]
    name: str
    price: float
    is_active: bool
    type: IngredientType = Field(validation_alias='ingredient_type')


class IngredientListResponseModel(BaseModel):
    ingredients: list[IngredientResponseModel]
    total_count: int


class IngredientTypeResponseModel(BaseModel):
    value: str
    name: str


class IngredientTypeListResponseModel(BaseModel):
    ingredient_types: list[IngredientTypeResponseModel]
    total_count: int


def get_ingredient_controller() -> IngredientController:
    """Dependency injection function for IngredientController"""
    container = Container()
    return IngredientController(
        ingredient_repository=container.ingredient_repository,
        presenter=JSONPresenter(),
    )


ingredient_router = APIRouter(tags=["ingredient"], prefix="/ingredient")


@ingredient_router.post("/create", response_model=IngredientResponseModel)
def create_ingredient(
    ingredient: IngredientCreateModel,
    controller: Annotated[IngredientController, Depends(get_ingredient_controller)],
) -> dict:
    """Create a new ingredient"""
    return controller.create_ingredient(ingredient.dict())


@ingredient_router.get("/list", response_model=IngredientListResponseModel)
def list_ingredients(
    controller: Annotated[IngredientController, Depends(get_ingredient_controller)],
    include_inactive: bool = False,
) -> dict:
    """List all ingredients"""
    return controller.list_ingredients(include_inactive=include_inactive)


@ingredient_router.get("/list/type/{ingredient_type}", response_model=IngredientListResponseModel)
def list_ingredients_by_type(
    ingredient_type: IngredientType,
    controller: Annotated[IngredientController, Depends(get_ingredient_controller)],
    include_inactive: bool = False,
) -> dict:
    """List ingredients by type"""
    return controller.list_ingredients_by_type(ingredient_type, include_inactive=include_inactive)


@ingredient_router.get("/list/applies-to", response_model=IngredientListResponseModel)
def list_ingredients_by_applies_to(
    controller: Annotated[IngredientController, Depends(get_ingredient_controller)],
    category: ProductCategory,
    include_inactive: bool = False,
) -> dict:
    """List ingredients by applies to"""
    return controller.list_ingredients_by_applies_to(
        category,
        include_inactive=include_inactive,
    )


@ingredient_router.get("/by-id/{ingredient_id}", response_model=IngredientResponseModel)
def get_ingredient(
    ingredient_id: int,
    controller: Annotated[IngredientController, Depends(get_ingredient_controller)],
    include_inactive: bool = False,
) -> dict:
    """Get an ingredient by ID"""
    return controller.get_ingredient(ingredient_id, include_inactive=include_inactive)


@ingredient_router.put("/update", response_model=IngredientResponseModel)
def update_ingredient(
    ingredient: IngredientUpdateModel,
    controller: Annotated[IngredientController, Depends(get_ingredient_controller)],
) -> dict:
    """Update an ingredient"""
    return controller.update_ingredient(ingredient.dict())


@ingredient_router.delete("/delete/{ingredient_id}")
def delete_ingredient(
    ingredient_id: int,
    controller: Annotated[IngredientController, Depends(get_ingredient_controller)],
) -> dict:
    """Delete an ingredient"""
    return controller.delete_ingredient(ingredient_id)


@ingredient_router.get("/types", response_model=IngredientTypeListResponseModel)
def list_ingredient_types(
    controller: Annotated[IngredientController, Depends(get_ingredient_controller)],
) -> dict:
    """List all ingredient types"""
    return controller.list_ingredient_types()