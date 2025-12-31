from src.entities.value_objects.email import Email
from src.entities.value_objects.name import Name
from src.entities.value_objects.document import Document
from src.entities.value_objects.money import Money
from src.entities.value_objects.sku import SKU
from decimal import Decimal

def test_email_domain_and_local_part():
    email = Email.create('user@domain.com')
    assert email.domain == 'domain.com'
    assert email.local_part == 'user'

def test_name_str_and_repr():
    name = Name.create('john doe')
    assert str(name) == 'John Doe'
    assert repr(name) == "Name('John Doe')"

def test_document_is_empty_and_formatted():
    doc = Document.create('52998224725')
    assert not doc.is_empty
    assert doc.formatted == '529.982.247-25'
    empty_doc = Document.create('')
    assert empty_doc.is_empty

def test_money_add_and_value():
    m1 = Money(amount=Decimal('10.00'))
    m2 = Money(amount=Decimal('5.00'))
    m3 = m1 + m2
    assert m3.amount == Decimal('15.00')
    assert m3.value == 15.0

def test_sku_str_and_repr():
    sku = SKU.create('SKU-1234-ABC')
    assert str(sku) == 'SKU-1234-ABC'
    assert repr(sku) == "SKU('SKU-1234-ABC')"
