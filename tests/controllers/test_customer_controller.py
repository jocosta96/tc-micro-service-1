import pytest
from src.adapters.controllers.customer_controller import CustomerController
from src.adapters.presenters.implementations.json_presenter import JSONPresenter

from src.entities.customer import Customer
from src.entities.value_objects.name import Name
from src.entities.value_objects.email import Email
from src.entities.value_objects.document import Document

class DummyCustomerRepository:
    def __init__(self):
        self._db = {}
        self._id = 1
    def save(self, customer):
        customer.internal_id = self._id
        self._db[self._id] = customer
        self._id += 1
        return customer
    def find_by_id(self, internal_id, include_inactive=False):
        return self._db.get(internal_id)
    def update(self, customer):
        if customer.internal_id in self._db:
            self._db[customer.internal_id] = customer
            return customer
        raise Exception('Not found')
    def delete(self, internal_id):
        if internal_id in self._db:
            del self._db[internal_id]
            return True
        return False
    def exists_by_document(self, document, include_inactive=False):
        return False
    def exists_by_email(self, email, include_inactive=False):
        return False

def controller():
    repo = DummyCustomerRepository()
    presenter = JSONPresenter()
    return CustomerController(repo, presenter), repo

def test_create_customer_success():
    ctrl, repo = controller()
    customer = Customer(
        internal_id=None,
        first_name=Name.create('John'),
        last_name=Name.create('Doe'),
        email=Email.create('john.doe@example.com'),
        document=Document.create('52998224725'),
           is_active=True,
           is_anonymous=False
    )
    saved = repo.save(customer)
    response = ctrl.get_customer(saved.internal_id)
    assert response['first_name'] == 'John'
    assert response['last_name'] == 'Doe'
    assert response['email'] == 'john.doe@example.com'

def test_create_customer_failure():
    ctrl, _ = controller()
    data = {}
    with pytest.raises(Exception):
        ctrl.create_customer(data)

def test_get_customer():
    ctrl, repo = controller()
    customer = Customer(
        internal_id=None,
        first_name=Name.create('Get'),
        last_name=Name.create('Test'),
        email=Email.create('get@example.com'),
        document=Document.create('52998224725'),
           is_active=True,
           is_anonymous=False
    )
    saved = repo.save(customer)
    response = ctrl.get_customer(saved.internal_id)
    assert response['first_name'] == 'Get'
    assert response['last_name'] == 'Test'

def test_update_customer():
    ctrl, repo = controller()
    customer = Customer(
        internal_id=None,
        first_name=Name.create('To'),
        last_name=Name.create('Update'),
        email=Email.create('update@example.com'),
        document=Document.create('52998224725'),
           is_active=True,
           is_anonymous=False
    )
    saved = repo.save(customer)
    updated_customer = Customer(
        internal_id=saved.internal_id,
        first_name=Name.create('Updated'),
        last_name=Name.create('Name'),
        email=Email.create('updated@example.com'),
        document=Document.create('52998224725'),
           is_active=True,
           is_anonymous=False
    )
    repo.update(updated_customer)
    response = ctrl.get_customer(saved.internal_id)
    assert response['first_name'] == 'Updated'
    assert response['last_name'] == 'Name'
    assert response['email'] == 'updated@example.com'

def test_delete_customer():
    ctrl, repo = controller()
    customer = Customer(
        internal_id=None,
        first_name=Name.create('To'),
        last_name=Name.create('Delete'),
        email=Email.create('delete@example.com'),
        document=Document.create('52998224725'),
           is_active=True,
           is_anonymous=False
    )
    saved = repo.save(customer)
    result = repo.delete(saved.internal_id)
    assert result is True
