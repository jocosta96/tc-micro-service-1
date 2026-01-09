from src.application.dto.implementation.customer_dto import CustomerCreateRequest, CustomerUpdateRequest, CustomerResponse, CustomerListResponse
from src.application.dto.implementation.ingredient_dto import IngredientCreateRequest, IngredientUpdateRequest, IngredientResponse, IngredientListResponse
from src.application.dto.implementation.product_dto import ProductCreateRequest, ProductUpdateRequest, ProductResponse, ProductListResponse
from datetime import datetime

def test_customer_create_request_to_dict():
    req = CustomerCreateRequest(first_name='A', last_name='B', email='a@b.com', document='52998224725')
    d = req.to_dict()
    assert d['first_name'] == 'A'

def test_customer_update_request_to_dict():
    req = CustomerUpdateRequest(internal_id=1, first_name='A', last_name='B', email='a@b.com', document='52998224725')
    d = req.to_dict()
    assert d['internal_id'] == 1

def test_customer_response_to_dict():
    resp = CustomerResponse(
        internal_id=1,
        first_name='A',
        last_name='B',
        email='a@b.com',
        document='52998224725',
        full_name='A B',
        is_anonymous=False,
        is_registered=True,
        is_active=True,
        created_at=datetime.utcnow()
    )
    d = resp.to_dict()
    assert d['internal_id'] == 1

def test_customer_list_response_to_dict():
    resp = CustomerListResponse(customers=[], total_count=0)
    d = resp.to_dict()
    assert 'data' in d

def test_ingredient_create_request_to_dict():
    req = IngredientCreateRequest(
        name='Sal', price=1.0, is_active=True, ingredient_type='sauce', applies_to_burger=True, applies_to_side=False, applies_to_drink=False, applies_to_dessert=False
    )
    d = req.to_dict()
    assert d['name'] == 'Sal'

def test_ingredient_update_request_to_dict():
    req = IngredientUpdateRequest(
        internal_id=1, name='Sal', price=1.0, is_active=True, ingredient_type='sauce', applies_to_burger=True, applies_to_side=False, applies_to_drink=False, applies_to_dessert=False
    )
    d = req.to_dict()
    assert d['internal_id'] == 1

def test_ingredient_response_to_dict():
    resp = IngredientResponse(
        internal_id=1, name='Sal', price=1.0, is_active=True, ingredient_type='sauce', applies_to_burger=True, applies_to_side=False, applies_to_drink=False, applies_to_dessert=False
    )
    d = resp.to_dict()
    assert d['name'] == 'Sal'

def test_ingredient_list_response_to_dict():
    resp = IngredientListResponse(ingredients=[], total_count=0)
    d = resp.to_dict()
    assert 'ingredients' in d

def test_product_create_request_to_dict():
    req = ProductCreateRequest(name='Prod', price=10.0, category='burger', sku='SKU-0001-ABC', default_ingredient=[])
    d = req.to_dict()
    assert d['name'] == 'Prod'

def test_product_update_request_to_dict():
    req = ProductUpdateRequest(internal_id=1, name='Prod', price=10.0, category='burger', sku='SKU-0001-ABC', default_ingredient=[])
    d = req.to_dict()
    assert d['internal_id'] == 1

def test_product_response_to_dict():
    resp = ProductResponse(internal_id=1, name='Prod', price=10.0, category='burger', sku='SKU-0001-ABC', is_active=True, default_ingredient=[])
    d = resp.to_dict()
    assert d['sku'] == 'SKU-0001-ABC'

def test_product_list_response_to_dict():
    resp = ProductListResponse(products=[], total_count=0)
    d = resp.to_dict()
    assert 'products' in d
