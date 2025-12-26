import pytest
from src.adapters.controllers.customer_controller import CustomerController

class DummyCustomerUseCase:
    def create_customer(self, data):
        if data.get('name'):
            return {'id': 1, 'name': data['name']}
        raise ValueError('Invalid data')

def test_create_customer_success():
    controller = CustomerController(DummyCustomerUseCase())
    data = {'name': 'John Doe'}
    response = controller.create_customer(data)
    assert response['id'] == 1
    assert response['name'] == 'John Doe'

def test_create_customer_failure():
    controller = CustomerController(DummyCustomerUseCase())
    data = {}
    with pytest.raises(ValueError):
        controller.create_customer(data)
