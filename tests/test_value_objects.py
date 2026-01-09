import pytest
from src.entities.value_objects.sku import SKU
from src.entities.value_objects.email import Email
from src.entities.value_objects.document import Document
from src.entities.value_objects.name import Name
from src.entities.value_objects.money import Money
from decimal import Decimal

# SKU

def test_valid_sku():
    sku = SKU.create('SKU-1234-ABC')
    assert sku.value == 'SKU-1234-ABC'

def test_invalid_sku():
    with pytest.raises(ValueError):
        SKU.create('INVALID')

# Email

def test_valid_email():
    email = Email.create('test@example.com')
    assert email.value == 'test@example.com'

def test_invalid_email():
    with pytest.raises(ValueError):
        Email.create('invalid-email')

# Document (CPF)

def test_valid_document():
    doc = Document.create('52998224725')
    assert doc.value == '52998224725'

def test_invalid_document():
    with pytest.raises(ValueError):
        Document.create('123')

# Name

def test_valid_name():
    name = Name.create('John Doe')
    assert name.value == 'John Doe'

def test_invalid_name():
    with pytest.raises(ValueError):
        Name.create('')

# Money

def test_valid_money():
    money = Money(amount=Decimal('10.50'))
    assert money.amount == Decimal('10.50')

def test_invalid_money():
    with pytest.raises(Exception):
        Money(amount='invalid')
