import pytest
from src.entities.customer import Customer
from src.entities.ingredient import Ingredient, IngredientType
from src.entities.product import Product, ProductCategory, ProductReceiptItem
from src.entities.value_objects.name import Name
from src.entities.value_objects.email import Email
from src.entities.value_objects.document import Document
from src.entities.value_objects.money import Money
from src.entities.value_objects.sku import SKU
from src.config.app_config import app_config

# Customer entity

def make_customer(**kwargs):
    is_anonymous = kwargs.get('is_anonymous', False)
    email = kwargs.get('email', None)
    if is_anonymous:
        email = app_config.anonymous_email
    if email is None:
        email = 'john.doe@example.com'
    return Customer(
        first_name=Name.create(kwargs.get('first_name', 'John')),
        last_name=Name.create(kwargs.get('last_name', 'Doe')),
        email=Email.create(email),
        document=Document.create(kwargs.get('document', '52998224725')),
        is_active=kwargs.get('is_active', True),
        is_anonymous=is_anonymous,
        internal_id=kwargs.get('internal_id'),
        created_at=kwargs.get('created_at'),
    )

def test_customer_full_name():
    c = make_customer(first_name='A', last_name='B')
    assert c.full_name == 'A B'

def test_customer_is_registered():
    c = make_customer(is_anonymous=False)
    assert c.is_registered is True
    c2 = make_customer(is_anonymous=True)
    assert c2.is_registered is False

def test_customer_can_place_order():
    c = make_customer(is_active=True, is_anonymous=False)
    assert c.can_place_order() is True
    c2 = make_customer(is_active=False)
    assert c2.can_place_order() is False
    c3 = make_customer(is_active=True, is_anonymous=True)
    assert c3.can_place_order() is True

def test_customer_get_display_name():
    c = make_customer(is_anonymous=True)
    assert c.get_display_name() == 'Anonymous Customer'
    c2 = make_customer(is_anonymous=False, first_name='A', last_name='B')
    assert c2.get_display_name() == 'A B'

def test_customer_str_repr():
    c = make_customer(internal_id=1)
    assert 'Customer' in str(c)
    assert 'Customer' in repr(c)

def test_customer_create_anonymous():
    c = Customer.create_anonymous(internal_id=5)
    assert c.is_anonymous is True
    assert c.internal_id == 5

def test_customer_create_registered():
    c = Customer.create_registered('A', 'B', 'a@b.com', '52998224725')
    assert c.is_anonymous is False
    assert c.first_name.value == 'A'

def test_customer_soft_delete():
    c = make_customer(internal_id=10, is_active=True, is_anonymous=False)
    c.soft_delete()
    assert c.is_active is False
    assert c.first_name.value == 'Deleted'
    assert 'deleted.10' in c.email.value

@pytest.mark.parametrize('kwargs,err', [({'is_anonymous':True,'email':'not@anon.com'}, ValueError), ({'is_anonymous':False,'email':''}, ValueError)])
def test_customer_business_rules_exceptions(kwargs, err):
    if kwargs.get('is_anonymous') and 'email' in kwargs:
        # Directly call Customer to bypass factory logic that overwrites email
        with pytest.raises(err):
            Customer(
                first_name=Name.create('John'),
                last_name=Name.create('Doe'),
                email=Email.create(kwargs['email']),
                document=Document.create('52998224725'),
                is_active=True,
                is_anonymous=True,
                internal_id=None,
                created_at=None,
            )
    else:
        with pytest.raises(err):
            make_customer(**kwargs)

# Ingredient entity

def make_ingredient(**kwargs):
    return Ingredient.create(
        name=kwargs.get('name', 'Sal'),
        price=Money(amount=kwargs.get('price', 1.0)),
        is_active=kwargs.get('is_active', True),
        ingredient_type=kwargs.get('ingredient_type', IngredientType.BREAD),
        applies_to_burger=kwargs.get('applies_to_burger', True),
        applies_to_side=kwargs.get('applies_to_side', False),
        applies_to_drink=kwargs.get('applies_to_drink', False),
        applies_to_dessert=kwargs.get('applies_to_dessert', False),
        internal_id=kwargs.get('internal_id'),
    )

def test_ingredient_str_repr():
    i = make_ingredient()
    assert 'Ingredient' in str(i)
    assert 'Ingredient' in repr(i)

@pytest.mark.parametrize('kwargs,expected_exception', [
    ({'name': ''}, ValueError),
    ({'price': None}, TypeError),
    ({'ingredient_type': None}, ValueError),
    ({'applies_to_burger': False, 'applies_to_side': False, 'applies_to_drink': False, 'applies_to_dessert': False}, ValueError),
    ({'applies_to_burger': True, 'ingredient_type': IngredientType.ICE}, ValueError),
    ({'applies_to_side': True, 'ingredient_type': IngredientType.BREAD}, ValueError),
    ({'applies_to_drink': True, 'ingredient_type': IngredientType.SAUCE}, ValueError),
    ({'applies_to_dessert': True, 'ingredient_type': IngredientType.SAUCE}, ValueError),
])
def test_ingredient_business_rules_exceptions(kwargs, expected_exception):
    with pytest.raises(expected_exception):
        make_ingredient(**kwargs)

# Product entity

def make_product(**kwargs):
    ingredient = make_ingredient()
    receipt_item = ProductReceiptItem(ingredient, 1)
    return Product.create(
        name=kwargs.get('name', 'Prod'),
        price=Money(amount=kwargs.get('price', 10.0)),
        category=kwargs.get('category', ProductCategory.BURGER),
        sku=SKU.create(kwargs.get('sku', 'SKU-0001-ABC')),
        default_ingredient=kwargs.get('default_ingredient', [receipt_item]),
        is_active=kwargs.get('is_active', True),
        internal_id=kwargs.get('internal_id'),
    )

def test_product_str_repr():
    p = make_product()
    assert 'Product' in str(p)
    assert 'Product' in repr(p)

def test_product_update():
    p = make_product()
    # For category 'side', ingredient must have applies_to_side=True and a valid type (e.g., BREAD)
    ingredient = Ingredient.create(
           name='SideIngredient',
           price=Money(amount=2.0),
           is_active=True,
           ingredient_type=IngredientType.SALAD,
           applies_to_burger=False,
           applies_to_side=True,
           applies_to_drink=False,
           applies_to_dessert=False,
           internal_id=None,
    )
    from src.entities.product import ProductReceiptItem
    receipt_item = ProductReceiptItem(ingredient, 1)
    p.update('Novo', 20.0, 'side', 'SKU-0002-DEF', [receipt_item])
    assert p.name.value == 'Novo'
    assert p.category == ProductCategory.SIDE

def test_product_business_rules_exceptions():
    ingredient = make_ingredient()
    receipt_item = ProductReceiptItem(ingredient, 1)
    with pytest.raises(ValueError):
        Product.create(
            name='', price=Money(amount=10.0), category=ProductCategory.BURGER, sku=SKU.create('SKU-0001-ABC'), default_ingredient=[receipt_item], is_active=True
        )
    with pytest.raises(ValueError):
        Product.create(
            name='Prod', price=None, category=ProductCategory.BURGER, sku=SKU.create('SKU-0001-ABC'), default_ingredient=[receipt_item], is_active=True
        )
    with pytest.raises(ValueError):
        Product.create(
            name='Prod', price=Money(amount=10.0), category=None, sku=SKU.create('SKU-0001-ABC'), default_ingredient=[receipt_item], is_active=True
        )
    with pytest.raises(ValueError):
        Product.create(
            name='Prod', price=Money(amount=10.0), category=ProductCategory.BURGER, sku=None, default_ingredient=[receipt_item], is_active=True
        )
    with pytest.raises(ValueError):
        Product.create(
            name='Prod', price=Money(amount=10.0), category=ProductCategory.BURGER, sku=SKU.create('SKU-0001-ABC'), default_ingredient=[], is_active=True
        )
