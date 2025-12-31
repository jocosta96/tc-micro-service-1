from src.application.use_cases.product_use_cases import (
    ProductCreateUseCase, ProductReadUseCase, ProductUpdateUseCase, ProductDeleteUseCase,
    ProductListUseCase, ProductListByCategoryUseCase
)
from src.application.dto.implementation.product_dto import ProductCreateRequest, ProductUpdateRequest

from src.entities.product import ProductCategory, ProductReceiptItem
from src.entities.ingredient import Ingredient, IngredientType
from src.entities.value_objects.name import Name
from src.entities.value_objects.money import Money

class DummyProductRepository:
    def exists_by_sku(self, sku):
        for product in self._db.values():
            if hasattr(product, 'sku') and product.sku == sku:
                return True
        return False
    def __init__(self):
        self._db = {}
        self._id = 1
    def save(self, product):
        product.internal_id = self._id
        self._db[self._id] = product
        self._id += 1
        return product
    def find_by_id(self, product_internal_id, include_inactive=False):
        return self._db.get(product_internal_id)
    def update(self, product):
        if product.internal_id in self._db:
            self._db[product.internal_id] = product
            return product
        raise Exception('Not found')
    def delete(self, product_internal_id):
        if product_internal_id in self._db:
            del self._db[product_internal_id]
            return True
        return False
    def find_all(self, include_inactive=False):
        return list(self._db.values())
    def find_by_sku(self, sku, include_inactive=False):
        return None
    def find_by_category(self, category):
        return list(self._db.values())

def test_product_create_and_read():
    repo = DummyProductRepository()
    create_uc = ProductCreateUseCase(repo)
    read_uc = ProductReadUseCase(repo)
    dummy_ingredient = Ingredient(
        name=Name('Dummy'),
        price=Money(1.0),
        is_active=True,
        ingredient_type=IngredientType.BREAD,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False,
        internal_id=1
    )
    default_ingredient = [ProductReceiptItem(dummy_ingredient, 1)]
    req = ProductCreateRequest(
        name='Produto', price=1.0, sku='SKU-1234-ABC', category=ProductCategory.BURGER, default_ingredient=default_ingredient
    )
    resp = create_uc.execute(req)
    assert resp.name == 'Produto'
    resp2 = read_uc.execute(resp.internal_id)
    assert resp2.name == 'Produto'

def test_product_update_and_delete():
    repo = DummyProductRepository()
    create_uc = ProductCreateUseCase(repo)
    update_uc = ProductUpdateUseCase(repo)
    delete_uc = ProductDeleteUseCase(repo)
    dummy_ingredient = Ingredient(
        name=Name('Dummy'),
        price=Money(1.0),
        is_active=True,
        ingredient_type=IngredientType.BREAD,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False,
        internal_id=1
    )
    default_ingredient = [ProductReceiptItem(dummy_ingredient, 1)]
    req = ProductCreateRequest(
        name='Produto', price=1.0, sku='SKU-1234-ABC', category=ProductCategory.BURGER, default_ingredient=default_ingredient
    )
    resp = create_uc.execute(req)
    upd_req = ProductUpdateRequest(
        internal_id=resp.internal_id, name='Produto Novo', price=2.0, sku='SKU-1234-ABC', category=ProductCategory.BURGER, default_ingredient=default_ingredient
    )
    resp2 = update_uc.execute(upd_req)
    assert resp2.name == 'Produto Novo'
    assert delete_uc.execute(resp2.internal_id) is True

def test_product_list_and_by_category():
    repo = DummyProductRepository()
    create_uc = ProductCreateUseCase(repo)
    list_uc = ProductListUseCase(repo)
    by_cat_uc = ProductListByCategoryUseCase(repo)
    dummy_ingredient = Ingredient(
        name=Name('Dummy'),
        price=Money(1.0),
        is_active=True,
        ingredient_type=IngredientType.BREAD,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False,
        internal_id=1
    )
    default_ingredient = [ProductReceiptItem(dummy_ingredient, 1)]
    req = ProductCreateRequest(
        name='Produto', price=1.0, sku='SKU-1234-ABC', category=ProductCategory.BURGER, default_ingredient=default_ingredient
    )
    create_uc.execute(req)
    assert list_uc.execute().total_count == 1
    assert by_cat_uc.execute(ProductCategory.BURGER).total_count == 1
