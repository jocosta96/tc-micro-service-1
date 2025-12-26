from fastapi import APIRouter, Depends
from typing_extensions import Annotated
from pydantic import BaseModel
from typing import Optional


from src.adapters.controllers.product_controller import ProductController
from src.adapters.di.container import Container
from src.entities.product import ProductCategory
from src.adapters.presenters.implementations.json_presenter import JSONPresenter


class ProductReceiptItemModel(BaseModel):
    ingredient_internal_id: int
    quantity: int


class ProductCreateModel(BaseModel):
    name: str
    price: float
    category: ProductCategory
    sku: str
    default_ingredient: list[ProductReceiptItemModel]
    is_active: bool


class ProductUpdateModel(BaseModel):
    internal_id: int
    name: str
    price: float
    category: ProductCategory
    sku: str
    default_ingredient: list[ProductReceiptItemModel]
    is_active: bool


class ProductResponseModel(BaseModel):
    internal_id: Optional[int]
    name: str
    price: float
    category: ProductCategory
    sku: str
    is_active: bool
    default_ingredient: list[dict]


class ProductListResponseModel(BaseModel):
    products: list[ProductResponseModel]
    total_count: int


def get_product_controller() -> ProductController:
    """Dependency injection function for ProductController"""
    container = Container()
    return ProductController(
        product_repository=container.product_repository,
        ingredient_repository=container.ingredient_repository,
        presenter=JSONPresenter(),
    )


product_router = APIRouter(tags=["product"], prefix="/product")


@product_router.post("/create", response_model=ProductResponseModel)
def create_product(
    product: ProductCreateModel,
    controller: Annotated[ProductController, Depends(get_product_controller)],
) -> dict:
    """Create a new product"""
    return controller.create_product(product.dict())


@product_router.get("/list", response_model=ProductListResponseModel)
def list_products(
    controller: Annotated[ProductController, Depends(get_product_controller)],
    include_inactive: bool = False,
) -> dict:
    """List all products"""
    return controller.list_products(include_inactive=include_inactive)


@product_router.get("/list/category/{category}", response_model=ProductListResponseModel)
def list_products_by_category(
    category: ProductCategory,
    controller: Annotated[ProductController, Depends(get_product_controller)],
    include_inactive: bool = False,
) -> dict:
    """List products by category"""
    return controller.list_products_by_category(category.value, include_inactive=include_inactive)


@product_router.get("/by-id/{product_id}", response_model=ProductResponseModel)
def get_product(
    product_id: int,
    controller: Annotated[ProductController, Depends(get_product_controller)],
    include_inactive: bool = False,
) -> dict:
    """Get a product by ID"""
    return controller.get_product(product_id, include_inactive=include_inactive)


@product_router.get("/by-sku/{sku}", response_model=ProductResponseModel)
def get_product_by_sku(
    sku: str,
    controller: Annotated[ProductController, Depends(get_product_controller)],
    include_inactive: bool = False,
) -> dict:
    """Get a product by SKU"""
    return controller.get_product_by_sku(sku, include_inactive=include_inactive)


@product_router.put("/update", response_model=ProductResponseModel)
def update_product(
    product: ProductUpdateModel,
    controller: Annotated[ProductController, Depends(get_product_controller)],
) -> dict:
    """Update a product"""
    return controller.update_product(product.dict())


@product_router.delete("/delete/{product_id}")
def delete_product(
    product_id: int,
    controller: Annotated[ProductController, Depends(get_product_controller)],
) -> dict:
    """Delete a product"""
    return controller.delete_product(product_id)
