import pytest
from src.application.repositories.customer_repository import CustomerRepository

class DummyDB:
    def insert(self, data):
        if data.get('name'):
            return 1
        raise Exception('DB error')

def test_customer_repository_add_success():
    repo = CustomerRepository(DummyDB())
    customer = {'name': 'Maria'}
    customer_id = repo.add(customer)
    assert customer_id == 1

def test_customer_repository_add_failure():
    repo = CustomerRepository(DummyDB())
    customer = {}
    with pytest.raises(Exception):
        repo.add(customer)
