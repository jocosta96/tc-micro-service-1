import pytest
from src.application.use_cases.customer_use_cases import CreateCustomerUseCase

class DummyCustomerRepository:
    def add(self, customer):
        return {'id': 1, **customer}

def test_create_customer_use_case_success():
    use_case = CreateCustomerUseCase(DummyCustomerRepository())
    data = {'name': 'Jane Doe'}
    result = use_case.create_customer(data)
    assert result['id'] == 1
    assert result['name'] == 'Jane Doe'

def test_create_customer_use_case_invalid():
    use_case = CreateCustomerUseCase(DummyCustomerRepository())
    data = {}
    with pytest.raises(Exception):
        use_case.create_customer(data)
