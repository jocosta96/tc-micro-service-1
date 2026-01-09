from src.application.dto.implementation.customer_dto import CustomerCreateRequest, CustomerUpdateRequest, CustomerResponse, CustomerListResponse
from src.application.dto.implementation.ingredient_dto import IngredientCreateRequest, IngredientUpdateRequest, IngredientResponse, IngredientListResponse
from src.application.dto.implementation.product_dto import ProductCreateRequest, ProductUpdateRequest, ProductResponse, ProductListResponse
from src.entities.ingredient import IngredientType
from datetime import datetime

def test_customer_create_request():
    req = CustomerCreateRequest(first_name='A', last_name='B', email='a@b.com', document='52998224725')
    assert req.first_name == 'A'
    assert req.last_name == 'B'
    assert req.email == 'a@b.com'
    assert req.document == '52998224725'

def test_customer_update_request():
    req = CustomerUpdateRequest(internal_id=1, first_name='A', last_name='B', email='a@b.com', document='52998224725')
    assert req.internal_id == 1


def test_customer_response():
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
    assert resp.is_active

def test_customer_list_response():
    resp = CustomerListResponse(customers=[], total_count=0)
    assert isinstance(resp.customers, list)



def test_ingredient_create_request():
    req = IngredientCreateRequest(
        name='Sal',
        price=1.0,
        is_active=True,
        ingredient_type=IngredientType.SAUCE,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False
    )
    assert req.name == 'Sal'
    assert req.price == 1.0
    assert req.is_active

def test_ingredient_update_request():
    req = IngredientUpdateRequest(
        internal_id=1,
        name='Sal',
        price=1.0,
        is_active=True,
        ingredient_type=IngredientType.SAUCE,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False
    )
    assert req.internal_id == 1

def test_ingredient_response():
    resp = IngredientResponse(
        internal_id=1,
        name='Sal',
        price=1.0,
        is_active=True,
        ingredient_type=IngredientType.SAUCE,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False
    )
    assert resp.name == 'Sal'

def test_ingredient_list_response():
    resp = IngredientListResponse(ingredients=[], total_count=0)
    assert isinstance(resp.ingredients, list)

def test_product_create_request():
    req = ProductCreateRequest(
        name='Prod',
        price=10.0,
        category='burger',
        sku='SKU-0001-ABC',
        default_ingredient=[]
    )
    assert req.name == 'Prod'
    assert req.price == 10.0
    assert req.category == 'burger'

def test_product_update_request():
    req = ProductUpdateRequest(
        internal_id=1,
        name='Prod',
        price=10.0,
        category='burger',
        sku='SKU-0001-ABC',
        default_ingredient=[]
    )
    assert req.internal_id == 1

def test_product_response():
    resp = ProductResponse(
        internal_id=1,
        name='Prod',
        price=10.0,
        category='burger',
        sku='SKU-0001-ABC',
        is_active=True,
        default_ingredient=[]
    )
    assert resp.sku == 'SKU-0001-ABC'

def test_product_list_response():
    resp = ProductListResponse(products=[], total_count=0)
    assert isinstance(resp.products, list)
