import json
from decimal import Decimal

import pytest

from src.app_logs import StructuredLogger, LogLevels, configure_logging
from src.config.app_config import app_config
from src.entities.customer import Customer
from src.entities.ingredient import Ingredient, IngredientType
from src.entities.product import Product, ProductCategory, ProductReceiptItem
from src.entities.value_objects.document import Document
from src.entities.value_objects.email import Email
from src.entities.value_objects.money import Money
from src.entities.value_objects.name import Name
from src.entities.value_objects.sku import SKU


def make_customer(**kwargs) -> Customer:
    return Customer(
        first_name=Name.create(kwargs.get("first_name", "John")),
        last_name=Name.create(kwargs.get("last_name", "Doe")),
        email=Email.create(kwargs.get("email", "john.doe@example.com")),
        document=Document.create(kwargs.get("document", "52998224725")),
        is_active=kwargs.get("is_active", True),
        is_anonymous=kwargs.get("is_anonymous", False),
        internal_id=kwargs.get("internal_id"),
    )


def make_ingredient(**kwargs) -> Ingredient:
    return Ingredient.create(
        name=kwargs.get("name", "Alface"),
        price=Money(amount=kwargs.get("price", Decimal("1.00"))),
        is_active=kwargs.get("is_active", True),
        ingredient_type=kwargs.get("ingredient_type", IngredientType.BREAD),
        applies_to_burger=kwargs.get("applies_to_burger", True),
        applies_to_side=kwargs.get("applies_to_side", False),
        applies_to_drink=kwargs.get("applies_to_drink", False),
        applies_to_dessert=kwargs.get("applies_to_dessert", False),
    )


def test_customer_soft_delete_invalid_states():
    inactive_customer = make_customer(is_active=False, internal_id=1)
    with pytest.raises(ValueError, match="inactive"):
        inactive_customer.soft_delete()

    no_id_customer = make_customer(internal_id=None)
    with pytest.raises(ValueError, match="without ID"):
        no_id_customer.soft_delete()

    anonymous_customer = make_customer(
        is_anonymous=True, email=app_config.anonymous_email, internal_id=1
    )
    with pytest.raises(ValueError, match="anonymous customer"):
        anonymous_customer.soft_delete()


def test_product_invalid_category_and_receipt_item_tuple():
    ingredient = make_ingredient(applies_to_burger=True)
    item = ProductReceiptItem(ingredient, 2)
    assert item.__tuple__() == (ingredient, 2)

    with pytest.raises((ValueError, TypeError)):
        Product(
            name=Name.create("X"),
            price=Money(amount=Decimal("1.00")),
            category="invalid",
            sku=SKU.create("ABC-1234-XYZ"),
            default_ingredient=[item],
            is_active=True,
        )

    not_drink_ingredient = make_ingredient(
        applies_to_burger=True,
        applies_to_drink=False,
        ingredient_type=IngredientType.BREAD,
    )
    bad_item = ProductReceiptItem(not_drink_ingredient, 1)
    with pytest.raises(ValueError, match="apply to drink"):
        Product.create(
            name="Juice",
            price=Money(amount=Decimal("5.00")),
            category=ProductCategory.DRINK,
            sku=SKU.create("DRK-1234-AAA"),
            default_ingredient=[bad_item],
            is_active=True,
        )


def test_money_decimal_places_and_add_with_decimal():
    with pytest.raises(ValueError):
        Money(amount=Decimal("1.234"))

    created = Money.create(Decimal("2.50"))
    assert created.amount == Decimal("2.50")

    base = Money(amount=Decimal("1.00"))
    result = base + Decimal("2.00")
    assert isinstance(result, Money)
    assert result.amount == Decimal("3.00")


def test_document_empty_and_check_digits():
    empty_doc = Document.create("")
    assert empty_doc.is_empty is True
    assert empty_doc.formatted == ""

    with pytest.raises(ValueError):
        Document.create("12345678901")  # Fails check digits despite correct length


def test_email_repr_and_missing_parts():
    email = Email.create("foo@bar.com")
    assert "foo@bar.com" in repr(email)

    empty_email = Email.create("")
    assert empty_email.domain == ""
    assert empty_email.local_part == ""


def test_name_too_long_triggers_validation():
    too_long = "A" * (app_config.max_name_length + 1)
    with pytest.raises(ValueError):
        Name.create(too_long)


def test_structured_logger_non_serializable_and_configure_logging_variants():
    class NoStr:
        def __getattribute__(self, item):
            if item == "__str__":
                raise AttributeError("no __str__")
            return super().__getattribute__(item)

    logger = StructuredLogger("phase1")
    payload = json.loads(logger._format_log("INFO", "msg", data=NoStr()))
    assert payload["message"] == "msg"
    assert "data" in payload

    configure_logging()  # uses default from app_config (covers log_level None path)
    configure_logging(LogLevels.debug)  # accepts enum and uses debug format path
