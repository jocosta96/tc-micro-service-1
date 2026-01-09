from unittest.mock import MagicMock
from src.adapters.gateways.sql_customer_repository import SQLCustomerRepository, CustomerModel

class DummyDatabase:
    def get_session(self):
        return MagicMock()
    def find_by_field(self, session, model, field, value):
        if field == "internal_id" and value == 1:
            m = MagicMock(spec=CustomerModel)
            m.internal_id = 1
            m.first_name = "John"
            m.last_name = "Doe"
            m.email = "john.doe@example.com"
            m.document = "52998224725"
            m.is_active = True
            m.is_anonymous = False
            m.created_at = None
            return m
        return None
    def find_all(self, session, model):
        return []
    def find_all_by_field(self, session, model, field, value):
        return []
    def add(self, session, obj):
        return obj
    def update(self, session, obj):
        return obj
    def commit(self, session):
        pass
    def rollback(self, session):
        pass
    def close_session(self, session):
        pass


def test_find_by_id_returns_customer():
    repo = SQLCustomerRepository(DummyDatabase())
    customer = repo.find_by_id(1)
    assert customer is not None
    assert customer.first_name.value == "John"
    assert customer.last_name.value == "Doe"
    assert customer.email.value == "john.doe@example.com"
    assert customer.document.value == "52998224725"

def test_find_by_id_returns_none():
    repo = SQLCustomerRepository(DummyDatabase())
    customer = repo.find_by_id(999)
    assert customer is None
