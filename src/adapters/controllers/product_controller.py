from fastapi import HTTPException
from http import HTTPStatus

from src.application.use_cases.product_use_cases import (
    ProductCreateUseCase,
    ProductReadUseCase,
    ProductUpdateUseCase,
    ProductDeleteUseCase,
    ProductListUseCase,
    ProductReadBySkuUseCase,
    ProductListByCategoryUseCase,
)
from src.application.dto import (
    ProductCreateRequest,
    ProductUpdateRequest,
)
from src.application.repositories.product_repository import ProductRepository
from src.application.repositories.ingredient_repository import IngredientRepository
from src.application.exceptions import (
    ProductNotFoundException,
    ProductAlreadyExistsException,
    ProductBusinessRuleException,
    ProductValidationException,
    AuthenticationException,
)
from src.adapters.presenters.interfaces.presenter_interface import PresenterInterface



class ProductController:
    """
    Product controller that handles HTTP requests.

    In Clean Architecture:
    - This is part of the Interface Adapters layer
    - It handles HTTP-specific concerns
    - It delegates business logic to use cases
    - It converts between HTTP data and application DTOs
    """

    def __init__(
        self, product_repository: ProductRepository, ingredient_repository: IngredientRepository, presenter: PresenterInterface
    ):
        self.product_repository = product_repository
        self.ingredient_repository = ingredient_repository
        self.presenter = presenter
        self.create_use_case = ProductCreateUseCase(product_repository)
        self.read_use_case = ProductReadUseCase(product_repository)
        self.update_use_case = ProductUpdateUseCase(product_repository)
        self.delete_use_case = ProductDeleteUseCase(product_repository)
        self.list_use_case = ProductListUseCase(product_repository)
        self.read_by_sku_use_case = ProductReadBySkuUseCase(product_repository)
        self.list_by_category_use_case = ProductListByCategoryUseCase(product_repository)


    def get_product(self, product_internal_id: int, include_inactive: bool = False) -> dict:
        """Get product by ID endpoint"""
        try:
            product = self.read_use_case.execute(product_internal_id, include_inactive=include_inactive)
            return self.presenter.present(product)
        except ProductNotFoundException as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_response)

    def create_product(self, product_data: dict) -> dict:
        """Create product endpoint"""
        try:
            # Convert default_ingredient from raw data to ProductReceiptItem objects
            default_ingredients = []
            raw_ingredients = product_data.get("default_ingredient", [])
            
            for ingredient_data in raw_ingredients:
                ingredient_id = ingredient_data.get("ingredient_internal_id")
                quantity = ingredient_data.get("quantity", 1)
                
                if ingredient_id:
                    # Convert string ID to int if needed
                    try:
                        ingredient_id = int(ingredient_id)
                    except (ValueError, TypeError):
                        pass
                    
                    # Fetch the ingredient from repository
                    ingredient = self.ingredient_repository.find_by_id(ingredient_id)
                    if ingredient:
                        from src.entities.product import ProductReceiptItem
                        default_ingredients.append(ProductReceiptItem(ingredient, quantity))
                    else:
                        raise ProductValidationException(f"Ingredient with ID {ingredient_id} not found")
                else:
                    raise ProductValidationException("Ingredient ID is required for each default ingredient")
            
            request = ProductCreateRequest(
                name=product_data.get("name", ""),
                price=product_data.get("price", ""),
                category=product_data.get("category", ""),
                sku=product_data.get("sku", ""),
                default_ingredient=default_ingredients,
            )
            product = self.create_use_case.execute(request)
            return self.presenter.present(product)
        except (
            ProductAlreadyExistsException,
            ProductBusinessRuleException,
            ProductValidationException,
        ) as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail=error_response
            )

    def update_product(self, product_data: dict) -> dict:
        """Update product endpoint"""
        try:
            # Convert default_ingredient from raw data to ProductReceiptItem objects
            default_ingredients = []
            raw_ingredients = product_data.get("default_ingredient", [])
            
            for ingredient_data in raw_ingredients:
                ingredient_id = ingredient_data.get("ingredient_internal_id")
                quantity = ingredient_data.get("quantity", 1)
                
                if ingredient_id:
                    # Convert string ID to int if needed
                    try:
                        ingredient_id = int(ingredient_id)
                    except (ValueError, TypeError):
                        pass
                    
                    # Fetch the ingredient from repository
                    ingredient = self.ingredient_repository.find_by_id(ingredient_id)
                    if ingredient:
                        from src.entities.product import ProductReceiptItem
                        default_ingredients.append(ProductReceiptItem(ingredient, quantity))
                    else:
                        raise ProductValidationException(f"Ingredient with ID {ingredient_id} not found")
                else:
                    raise ProductValidationException("Ingredient ID is required for each default ingredient")
            
            request = ProductUpdateRequest(
                internal_id=product_data.get("internal_id"),
                name=product_data.get("name", ""),
                price=product_data.get("price", ""),
                category=product_data.get("category", ""),
                sku=product_data.get("sku", ""),
                default_ingredient=default_ingredients,
            )
            product = self.update_use_case.execute(request)
            return self.presenter.present(product)
        except (
            ProductNotFoundException,
            ProductAlreadyExistsException,
            ProductBusinessRuleException,
            ProductValidationException,
        ) as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail=error_response
            )

    def delete_product(self, product_internal_id: int) -> dict:
        """Delete product endpoint"""
        try:
            success = self.delete_use_case.execute(product_internal_id)
            return self.presenter.present(
                {"success": success, "message": "Product soft deleted successfully"}
            )
        except (ProductNotFoundException, ProductBusinessRuleException) as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_response)

    def list_products(self, include_inactive: bool = False) -> dict:
        """List all products endpoint"""
        try:
            product_list = self.list_use_case.execute(include_inactive=include_inactive)
            return self.presenter.present(product_list)
        except Exception as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=error_response
            )
    
    def get_product_by_name(self, name: str, include_inactive: bool = False) -> dict:
        """Get product by name endpoint"""
        
        try:
            # Note: This would need a ProductReadByNameUseCase to be implemented
            # For now, we'll use the list use case and filter by name
            products = self.list_use_case.execute(include_inactive=include_inactive)
            product_list = products.products if hasattr(products, 'products') else products
            product = next((p for p in product_list if p.name == name), None)
            
            if not product:
                raise ProductNotFoundException(f"Product with name {name} not found")
                
            return self.presenter.present(product)
        except ProductNotFoundException as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_response)
        except ProductBusinessRuleException as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=error_response)
    
    def get_product_by_category(self, category: str, include_inactive: bool = False) -> dict:
        """Get product by category endpoint"""        
        try:
            products = self.list_by_category_use_case.execute(category, include_inactive=include_inactive)
            return self.presenter.present(products)
        except ProductNotFoundException as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_response)
        except ProductBusinessRuleException as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=error_response)

    def get_product_by_sku(self, sku: str, include_inactive: bool = False) -> dict:
        """Get product by sku endpoint"""
        
        try:
            product = self.read_by_sku_use_case.execute(sku, include_inactive=include_inactive)
            return self.presenter.present(product)
        except ProductNotFoundException as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_response)
        except ProductBusinessRuleException as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=error_response)

    def list_products_by_category(self, category: str, include_inactive: bool = False) -> dict:
        """List products by category endpoint"""        
        try:
            product_list = self.list_by_category_use_case.execute(category, include_inactive=include_inactive)
            return self.presenter.present(product_list)
        except ProductNotFoundException as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_response)
        except ProductBusinessRuleException as e:
            error_response = self.presenter.present_error(e)
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=error_response)
