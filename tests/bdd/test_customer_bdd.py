import pytest
from pytest_bdd import scenarios, given, when, then
from src.adapters.controllers.customer_controller import CustomerController
from src.adapters.presenters.implementations.json_presenter import JSONPresenter

scenarios('customer.feature')

class DummyCustomerRepository:
    def find_by_email(self, email, include_inactive=False):
        for customer in self._db.values():
            if hasattr(customer, 'email') and getattr(customer.email, 'value', None) == email:
                return customer
        return None
    
    def find_by_document(self, document, include_inactive=False):
        for customer in self._db.values():
            if hasattr(customer, 'document') and getattr(customer.document, 'value', None) == document:
                return customer
        return None
    
    def __init__(self):
        self._db = {}
        self._id = 1
    def save(self, customer):
        customer.internal_id = self._id
        if not hasattr(customer, 'is_anonymous'):
            customer.is_anonymous = False
        self._db[self._id] = customer
        self._id += 1
        return customer
    def find_by_id(self, customer_internal_id, include_inactive=False):
        return self._db.get(customer_internal_id)
    def update(self, customer):
        if customer.internal_id in self._db:
            self._db[customer.internal_id] = customer
            return customer
        raise Exception('Not found')
    def delete(self, customer_internal_id):
        if customer_internal_id in self._db:
            del self._db[customer_internal_id]
            return True
        return False
    def exists_by_document(self, document, include_inactive=False):
        return False
    def exists_by_email(self, email, include_inactive=False):
        return False

@pytest.fixture(scope='module')
def controller():
    repo = DummyCustomerRepository()
    presenter = JSONPresenter()
    return CustomerController(repo, presenter), repo


# Step definition for BDD, just marks the step
@given('que o payload do cliente é válido')
def given_payload_cliente():
    pass

# Pytest fixture for payload_cliente
@pytest.fixture
def payload_cliente():
    return {
        'first_name': 'Cliente',
        'last_name': 'BDD',
        'email': 'cliente.bdd@example.com',
        'document': '52998224725'  # CPF válido
    }

@when('eu crio o cliente')
def criar_cliente(controller, payload_cliente, request):
    ctrl, _ = controller
    response = ctrl.create_customer(payload_cliente)
    request.customer_id = response['internal_id']
    request.customer_data = response

@then('o cliente é criado com sucesso')
def cliente_criado(request):
    assert request.customer_id is not None
    assert request.customer_data['first_name'] == 'Cliente'
    assert request.customer_data['last_name'] == 'Bdd'

@when('eu consulto o cliente')
def consultar_cliente(controller, request):
    ctrl, _ = controller
    response = ctrl.get_customer(request.customer_id)
    request.customer_data = response

@then('os dados do cliente estão corretos')
def dados_cliente_corretos(request):
    assert request.customer_data['first_name'] == 'Cliente'
    assert request.customer_data['last_name'] == 'Bdd'
    assert request.customer_data['email'] == 'cliente.bdd@example.com'

@when('eu atualizo o cliente')
def atualizar_cliente(controller, request):
    ctrl, _ = controller
    update_req = {
        'internal_id': request.customer_id,
        'first_name': 'Cliente',
        'last_name': 'BDD Atualizado',
        'email': 'cliente.bdd2@example.com',
        'document': '52998224725'
    }
    response = ctrl.update_customer(update_req)
    request.customer_data = response

@then('o cliente é atualizado com sucesso')
def cliente_atualizado(request):
    assert request.customer_data['last_name'] == 'Bdd Atualizado'
    assert request.customer_data['email'] == 'cliente.bdd2@example.com'

@when('eu deleto o cliente')
def deletar_cliente(controller, request):
    ctrl, _ = controller
    response = ctrl.delete_customer(request.customer_id)
    request.delete_result = response

@then('o cliente é deletado com sucesso')
def cliente_deletado(request):
    assert "'success': True" in request.delete_result['data']