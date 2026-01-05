import pytest
from src.entities.value_objects.sku import SKU
from src.entities.value_objects.email import Email
from src.entities.value_objects.name import Name
from src.entities.value_objects.document import Document
from src.entities.value_objects.money import Money
from decimal import Decimal

# SKU edge cases
def test_invalid_sku_raises():
    with pytest.raises(ValueError):
        SKU.create("")
    with pytest.raises(ValueError):
        SKU.create("ABC-123-XYZ")  # Invalid: does not match required format

def test_sku_str_repr():
    sku = SKU.create("ABC-1234-XYZ")  # Valid: matches required format
    assert str(sku) == "ABC-1234-XYZ"
    assert "SKU" in repr(sku)

# Email edge cases
def test_invalid_email_raises():
    with pytest.raises(ValueError):
           Email.create("invalidemail.com")  # Missing '@' and domain
    with pytest.raises(ValueError):
        Email.create("invalidemail.com")

def test_email_domain_local_part():
    email = Email.create("foo@bar.com")
    assert email.domain == "bar.com"
    assert email.local_part == "foo"

# Name edge cases
def test_invalid_name_raises():
    with pytest.raises(ValueError):
        Name.create("")
    with pytest.raises(ValueError):
        Name.create(" ")

def test_name_str_repr():
    name = Name.create("John Doe")
    assert str(name) == "John Doe"
    assert "John Doe" in repr(name)

# Document edge cases
def test_invalid_document_raises():
    with pytest.raises(ValueError):
        Document.create("11111111111")  # Invalid: all digits the same
    with pytest.raises(ValueError):
        Document.create("12345678900")  # Invalid: fails check digits

def test_document_is_empty_and_formatted():
    doc = Document.create("12345678909")
    assert not doc.is_empty
    assert isinstance(doc.formatted, str)

# Money edge cases
def test_invalid_money_raises():
    with pytest.raises(ValueError):
        Money(Decimal("-1"))

def test_money_str_repr():
    m = Money(Decimal("10.00"))
    assert "Money" in repr(m)
