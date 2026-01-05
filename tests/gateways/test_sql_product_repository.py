import pytest

from src.adapters.gateways.sql_product_repository import ProductModel, SQLProductRepository
from src.entities.ingredient import Ingredient, IngredientType
from src.entities.product import Product, ProductCategory, ProductReceiptItem
from src.entities.value_objects.money import Money
from src.entities.value_objects.sku import SKU
from tests.gateways.stub_database import InMemoryDatabase


class IngredientRepoStub:
    def __init__(self, ingredient: Ingredient):
        self.ingredient = ingredient

    def find_by_id(self, internal_id: int, include_inactive: bool = False):
        if self.ingredient and self.ingredient.internal_id == internal_id:
            return self.ingredient
        return None


def _make_ingredient(internal_id: int, applies_to_burger: bool = True, is_active: bool = True) -> Ingredient:
    return Ingredient.create(
        name="Cheese",
        price=Money(amount=2.5),
        is_active=is_active,
        ingredient_type=IngredientType.CHEESE,
        applies_to_burger=applies_to_burger,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False,
        internal_id=internal_id,
    )


def test_to_entity_converts_default_ingredients_with_repo_lookup():
    db = InMemoryDatabase()
    ingredient = _make_ingredient(1)
    repo = SQLProductRepository(db, IngredientRepoStub(ingredient))

    model = ProductModel(
        internal_id=5,
        name="Burger",
        price=15.0,
        category="burger",
        sku="BRG-0001-ABC",
        default_ingredient=[{"ingredient_internal_id": ingredient.internal_id, "quantity": 2}],
        is_active=True,
    )

    entity = repo._to_entity(model)

    assert entity.internal_id == 5
    assert entity.default_ingredient[0].ingredient.internal_id == ingredient.internal_id
    assert entity.default_ingredient[0].quantity == 2


def test_to_entity_raises_when_no_default_ingredient():
    db = InMemoryDatabase()
    repo = SQLProductRepository(db, IngredientRepoStub(_make_ingredient(1)))

    model = ProductModel(
        internal_id=1,
        name="Burger",
        price=10.0,
        category="burger",
        sku="BRG-0002-XYZ",
        default_ingredient=[],
        is_active=True,
    )

    with pytest.raises(ValueError):
        repo._to_entity(model)


def test_save_new_product_commits_and_serializes_default_ingredient():
    db = InMemoryDatabase()
    ingredient = _make_ingredient(10)
    repo = SQLProductRepository(db, IngredientRepoStub(ingredient))

    product = Product.create(
        name="Combo",
        price=Money(amount=20.0),
        category=ProductCategory.BURGER,
        sku=SKU.create("BRG-0003-ABC"),
        default_ingredient=[ProductReceiptItem(ingredient, 1)],
        is_active=True,
    )

    saved = repo.save(product)

    assert saved.internal_id == 1
    assert db.committed is True
    stored_model = db.store[ProductModel][0]
    assert stored_model.default_ingredient[0]["ingredient_internal_id"] == ingredient.internal_id


def test_save_rolls_back_when_conversion_fails_after_commit():
    db = InMemoryDatabase()
    ingredient_without_id = _make_ingredient(internal_id=None, applies_to_burger=True)  # type: ignore[arg-type]
    repo = SQLProductRepository(db, IngredientRepoStub(ingredient_without_id))

    product = Product.create(
        name="Invalid Combo",
        price=Money(amount=20.0),
        category=ProductCategory.BURGER,
        sku=SKU.create("BRG-9999-ERR"),
        default_ingredient=[ProductReceiptItem(ingredient_without_id, 1)],
        is_active=True,
    )

    with pytest.raises(ValueError):
        repo.save(product)

    assert db.rolled_back is True
    assert db.committed is False


def test_find_by_sku_respects_include_inactive_and_conversion_errors():
    db = InMemoryDatabase()
    ingredient = _make_ingredient(1, applies_to_burger=True, is_active=False)
    repo = SQLProductRepository(db, IngredientRepoStub(ingredient))
    session = db.get_session()

    inactive_model = ProductModel(
        internal_id=1,
        name="Inactive",
        price=5.0,
        category="burger",
        sku="BRG-0010-OFF",
        default_ingredient=[{"ingredient_internal_id": ingredient.internal_id, "quantity": 1}],
        is_active=False,
    )
    active_model = ProductModel(
        internal_id=2,
        name="Active",
        price=5.0,
        category="burger",
        sku="BRG-0011-AAA",
        default_ingredient=[{"ingredient_internal_id": ingredient.internal_id, "quantity": 1}],
        is_active=True,
    )
    db.add(session, inactive_model)
    db.add(session, active_model)

    assert repo.find_by_sku(SKU.create("BRG-0010-OFF")) is None
    assert repo.find_by_sku(SKU.create("BRG-0010-OFF"), include_inactive=True) is not None
    assert repo.find_by_sku(SKU.create("BRG-0011-AAA")).internal_id == 2


def test_find_all_skips_models_that_cannot_be_converted():
    db = InMemoryDatabase()
    ingredient = _make_ingredient(1)
    repo = SQLProductRepository(db, IngredientRepoStub(ingredient))
    session = db.get_session()

    invalid_model = ProductModel(
        internal_id=1,
        name="Broken",
        price=5.0,
        category="burger",
        sku="BRG-0020-BAD",
        default_ingredient=[],  # triggers conversion error
        is_active=True,
    )
    valid_model = ProductModel(
        internal_id=2,
        name="Working",
        price=8.0,
        category="burger",
        sku="BRG-0021-ABC",
        default_ingredient=[{"ingredient_internal_id": ingredient.internal_id, "quantity": 1}],
        is_active=True,
    )
    db.add(session, invalid_model)
    db.add(session, valid_model)

    results = repo.find_all()

    assert len(results) == 1
    assert results[0].internal_id == 2
