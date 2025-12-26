import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from src.adapters.controllers.customer_controller import CustomerController

scenarios('customer.feature')

class DummyCustomerUseCase:
    def create_customer(self, data):
        if data.get('name'):
            return {'id': 1, 'name': data['name']}
        raise ValueError('Invalid data')

@given('que o payload do cliente é válido')
def valid_payload():
    return {'name': 'Cliente BDD'}

@when('eu envio uma requisição de cadastro')
def send_create_request(valid_payload):
    controller = CustomerController(DummyCustomerUseCase())
    return controller.create_customer(valid_payload)

@then('o cliente é criado com sucesso')
def check_created(send_create_request):
    assert send_create_request['id'] == 1
    assert send_create_request['name'] == 'Cliente BDD'
