from src.application.repositories.product_repository import ProductRepository
from src.application.dto.implementation.product_dto import ProductCreateRequest, ProductUpdateRequest, ProductListResponse, ProductResponse
from src.application.exceptions import ProductNotFoundException, ProductAlreadyExistsException, ProductValidationException
from src.entities.product import Product, ProductCategory
from src.entities.value_objects.sku import SKU
from src.app_logs import get_logger


class ProductCreateUseCase:
    """
    Use case for creating a new product.

    This use case:
    - Contains business logic for product creation
    - Validates business rules
    - Orchestrates between domain and repository
    - Is independent of infrastructure (uses repository interface)
    """

    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
        self.logger = get_logger("ProductCreateUseCase")

    def execute(self, request: ProductCreateRequest) -> ProductResponse:
        """Execute the create product use case"""
        self.logger.info(
            "Creating new product", name=request.name, price=request.price, category=request.category, sku=request.sku)

        # Create product entity from DTO
        product = Product.create_registered(
            name=request.name,
            price=request.price,
            category=request.category,
            sku=request.sku,
            default_ingredient=request.default_ingredient,
        )

        # Business rule: Check if product with same SKU already exists
        if self.product_repository.exists_by_sku(product.sku):
            self.logger.warning(
                "Product creation failed - SKU already exists", sku=product.sku)
            raise ProductAlreadyExistsException(
                f"Product with SKU {product.sku} already exists")

        # Save product to repository
        saved_product = self.product_repository.save(product)

        # Return product response
        return ProductResponse.from_entity(saved_product)


class ProductReadUseCase:
    """
    Use case for reading a product.
    """

    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
        self.logger = get_logger("ProductReadUseCase")

    def execute(self, product_internal_id: int, include_inactive: bool = False) -> ProductResponse:
        """Execute the read product use case"""
        self.logger.info("Reading product", product_internal_id=product_internal_id)

        # Find product by ID
        product = self.product_repository.find_by_id(product_internal_id, include_inactive=include_inactive)

        if not product:
            self.logger.warning("Product not found", product_internal_id=product_internal_id)
            raise ProductNotFoundException(
                f"Product with internal_id {product_internal_id} not found")

        # Return product response
        return ProductResponse.from_entity(product)

class ProductUpdateUseCase:
    """
    Use case for updating a product.
    """

    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
        self.logger = get_logger("ProductUpdateUseCase")

    def execute(self, request: ProductUpdateRequest) -> ProductResponse:
        """Execute the update product use case"""
        self.logger.info("Updating product", product_internal_id=request.internal_id)

        # Find product by ID (include inactive for updates)
        product = self.product_repository.find_by_id(request.internal_id, include_inactive=True)

        if not product:
            self.logger.warning("Product not found", product_internal_id=request.internal_id)
            raise ProductNotFoundException(
                f"Product with internal_id {request.internal_id} not found")

        # Update product entity from DTO
        product.update(
            name=request.name,
            price=request.price,
            category=request.category,
            sku=request.sku,
            default_ingredient=request.default_ingredient,
        )

        # Business rule: Check if product with same SKU already exists (exclude current product)
        existing_product_with_sku = self.product_repository.find_by_sku(product.sku, include_inactive=True)
        if existing_product_with_sku and existing_product_with_sku.internal_id != request.internal_id:
            self.logger.warning(
                "Product update failed - SKU already exists", sku=product.sku)
            raise ProductAlreadyExistsException(
                f"Product with SKU {product.sku} already exists")

        # Save product to repository
        self.product_repository.save(product)

        # Return product response
        return ProductResponse.from_entity(product)

class ProductDeleteUseCase:
    """
    Use case for deleting a product.
    """

    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
        self.logger = get_logger("ProductDeleteUseCase")

    def execute(self, product_internal_id: int) -> bool:
        """Execute the delete product use case"""
        self.logger.info("Deleting product", product_internal_id=product_internal_id)

        # Find product by ID (include inactive for deletion)
        product = self.product_repository.find_by_id(product_internal_id, include_inactive=True)

        if not product:
            self.logger.warning("Product not found", product_internal_id=product_internal_id)
            raise ProductNotFoundException(
                f"Product with internal_id {product_internal_id} not found")

        # Soft delete product from repository
        self.product_repository.delete(product_internal_id)

        return True

class ProductListUseCase:
    """
    Use case for listing products.
    """

    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
        self.logger = get_logger("ProductListUseCase")

    def execute(self, include_inactive: bool = False) -> ProductListResponse:
        """Execute the list product use case"""
        self.logger.info("Listing products", include_inactive=include_inactive)

        # Find all products
        products = self.product_repository.find_all(include_inactive=include_inactive)

        # Return product list response
        return ProductListResponse.from_entity(products)

class ProductReadBySkuUseCase:
    """
    Use case for reading a product by SKU.
    """

    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
        self.logger = get_logger("ProductReadBySkuUseCase")

    def execute(self, sku: str, include_inactive: bool = False) -> ProductResponse:
        """Execute the read product by SKU use case"""
        self.logger.info("Reading product by SKU", sku=sku)

        # Create SKU value object
        sku_obj = SKU(sku)

        # Find product by SKU
        product = self.product_repository.find_by_sku(sku_obj, include_inactive=include_inactive)

        if not product:
            self.logger.warning("Product not found", sku=sku)
            raise ProductNotFoundException(
                f"Product with SKU {sku} not found")

        # Return product response
        return ProductResponse.from_entity(product)

class ProductListByCategoryUseCase:
    """
    Use case for listing products by category.
    """

    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
        self.logger = get_logger("ProductListByCategoryUseCase")

    def execute(self, category: str, include_inactive: bool = False) -> ProductListResponse:
        """Execute the list products by category use case"""
        self.logger.info("Listing products by category", category=category)

        # Convert string to ProductCategory enum
        try:
            product_category = ProductCategory(category)
        except ValueError:
            raise ProductValidationException(f"Invalid category: {category}")

        # Find all products and filter by category
        all_products = self.product_repository.find_all(include_inactive=include_inactive)
        filtered_products = [p for p in all_products if p.category == product_category]

        # Return product list response
        return ProductListResponse.from_entity(filtered_products)