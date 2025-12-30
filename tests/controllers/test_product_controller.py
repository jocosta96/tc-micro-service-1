import pytest

from src.entities.value_objects.money import Money
from src.entities.product import Product, ProductReceiptItem
from src.entities.ingredient import Ingredient, IngredientType
from src.adapters.controllers.product_controller import ProductController
from src.adapters.presenters.implementations.json_presenter import JSONPresenter

class DummyProductRepository:
    def find_by_sku(self, sku, include_inactive=False):
        # Return the first product with matching SKU, or None
        for product in self._db.values():
            if hasattr(product, 'sku') and product.sku == sku:
                return product
        return None
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
    def exists_by_sku(self, sku, include_inactive=False):
        return False

@pytest.fixture(scope='module')
def controller():
    repo = DummyProductRepository()
    # Dummy ingredient repo for required argument
    class DummyIngredientRepo:
        def find_by_id(self, ingredient_internal_id, include_inactive=False):
            # Return a dummy ingredient for any id
            from src.entities.value_objects.money import Money
            from src.entities.value_objects.name import Name
            from src.entities.ingredient import Ingredient, IngredientType
            return Ingredient.create(
                name='Pão',
                price=Money(amount=1.0),
                is_active=True,
                ingredient_type=IngredientType.BREAD,
                applies_to_burger=True,
                applies_to_side=False,
                applies_to_drink=False,
                applies_to_dessert=False
            )
    ingredient_repo = DummyIngredientRepo()
    presenter = JSONPresenter()
    ctrl = ProductController(repo, ingredient_repo, presenter)
    return ctrl, repo

def test_create_product(controller):
    ctrl, repo = controller
    # Pass default_ingredient as list of dicts for controller
    default_ingredient = [{
        'ingredient_internal_id': 1,
        'quantity': 1
    }]
    payload = {
        'name': 'Produto A',
        'price': 10.0,
        'category': 'burger',
        'sku': 'SKU-0001-ABC',
        'default_ingredient': default_ingredient
    }
    response = ctrl.create_product(payload)
    assert response['name'] == 'Produto A'
    assert response['sku'] == 'SKU-0001-ABC'
    assert response['price'] == 10.0

def test_get_product(controller):
    ctrl, repo = controller
    from src.entities.value_objects.money import Money
    from src.entities.value_objects.name import Name
    from src.entities.value_objects.sku import SKU
    from src.entities.product import Product, ProductCategory, ProductReceiptItem
    from src.entities.ingredient import Ingredient, IngredientType
    ingredient = Ingredient.create(
        name='Pão',
        price=Money(amount=1.0),
        is_active=True,
        ingredient_type=IngredientType.BREAD,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False
    )
    receipt_item = ProductReceiptItem(ingredient, 1)
    # Use valid SKU format
    payload = {
        'name': 'Produto B',
        'price': 20.0,
        'category': 'burger',
        'sku': 'SKU-0002-DEF',
        'default_ingredient': [receipt_item]
    }
    product = repo.save(Product.create_registered(**payload))
    response = ctrl.get_product(product.internal_id)
    assert response['name'] == 'Produto B'
    assert response['sku'] == 'SKU-0002-DEF'
    assert response['price'] == 20.0

def test_update_product(controller):
    ctrl, repo = controller
    ingredient = Ingredient.create(
        name='Pão',
        price=Money(amount=1.0),
        is_active=True,
        ingredient_type=IngredientType.BREAD,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False
    )
    # Use list of dicts for default_ingredient, as expected by controller
    # For direct Product.create_registered, use ProductReceiptItem objects
    receipt_item = ProductReceiptItem(ingredient, 1)
    payload = {
        'name': 'Produto C',
        'price': 30.0,
        'category': 'burger',
        'sku': 'SKU-0003-GHI',
        'default_ingredient': [receipt_item]
    }
    product = repo.save(Product.create_registered(**payload))
    # For controller, use dicts as before
    update_payload = {
        'internal_id': product.internal_id,
        'name': 'Produto C Atualizado',
        'price': 35.0,
        'category': 'burger',
        'sku': 'SKU-0003-GHI',
        'default_ingredient': [{
            'ingredient_internal_id': 1,
            'quantity': 1
        }]
    }
    response = ctrl.update_product(update_payload)
    assert response['name'] == 'Produto C Atualizado'
    assert response['price'] == 35.0

def test_delete_product(controller):
    ctrl, repo = controller
    ingredient = Ingredient.create(
        name='Pão',
        price=Money(amount=1.0),
        is_active=True,
        ingredient_type=IngredientType.BREAD,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False
    )
    # For direct Product.create_registered, use ProductReceiptItem objects
    receipt_item = ProductReceiptItem(ingredient, 1)
    payload = {
        'name': 'Produto D',
        'price': 40.0,
        'category': 'burger',
        'sku': 'SKU-0004-JKL',
        'default_ingredient': [receipt_item]
    }
    product = repo.save(Product.create_registered(**payload))
    result = ctrl.delete_product(product.internal_id)
    # The controller returns a dict, check for success message
    assert isinstance(result, dict)
    assert 'success' in str(result['data'])
