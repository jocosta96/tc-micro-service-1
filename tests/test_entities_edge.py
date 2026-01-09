import pytest
from src.entities.ingredient import Ingredient, IngredientType
from src.entities.value_objects.name import Name
from src.entities.value_objects.money import Money
from src.entities.product import Product, ProductCategory, ProductReceiptItem
from src.entities.value_objects.sku import SKU
from decimal import Decimal

def test_ingredient_business_rules():
    name = Name.create("Alface")
    price = Money(Decimal("1.00"))
    ing = Ingredient(
        name=name,
        ingredient_type=IngredientType.VEGETABLE,
        price=price,
        is_active=True,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False
    )
    assert ing.ingredient_type == IngredientType.VEGETABLE
    assert str(ing)
    assert repr(ing)

    # Test invalid type
    with pytest.raises(ValueError):
        Ingredient(
            name=name,
            ingredient_type="invalid",
            price=price,
            is_active=True,
            applies_to_burger=True,
            applies_to_side=False,
            applies_to_drink=False,
            applies_to_dessert=False
        )

    # Test create factory
    ing2 = Ingredient.create(
        name="Alface",
        ingredient_type=IngredientType.BREAD,
        price=price,
        is_active=True,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False
    )
    assert isinstance(ing2, Ingredient)

def test_product_business_rules():
    name = Name.create("Pao")
    price = Money(Decimal("2.00"))
    ing = Ingredient(
        name=name,
        ingredient_type=IngredientType.SALAD,
        price=price,
        is_active=True,
        applies_to_burger=True,
        applies_to_side=True,
        applies_to_drink=False,
        applies_to_dessert=False
    )
    item = ProductReceiptItem(ingredient=ing, quantity=2)
    prod = Product(name=name, category=ProductCategory.BURGER, price=price, default_ingredient=[item], sku=SKU.create("ABC-1234-XYZ"), is_active=True)
    assert prod.category == ProductCategory.BURGER
    assert str(prod)
    assert repr(prod)
    # Test create factory
    prod2 = Product.create(name="Pao", category=ProductCategory.SIDE, price=price, default_ingredient=[item], sku=SKU.create("ABC-1234-XYZ"), is_active=True)
    assert isinstance(prod2, Product)
    # Test update
    prod2.update(
        name="Novo Pao",
        price=Decimal("2.00"),
        category=ProductCategory.SIDE,
        sku="ABC-1234-XYZ",
        default_ingredient=[item]
    )
    assert prod2.name == Name.create("Novo Pao")
