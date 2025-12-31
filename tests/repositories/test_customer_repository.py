import pytest

class DummyCustomerRepository:
    def __init__(self):
        self._db = {}
        self._id = 1
    def add(self, customer):
        if not customer.get('name'):
            raise Exception('Invalid customer')
        customer['internal_id'] = self._id
        self._db[self._id] = customer
        self._id += 1
        return customer['internal_id']
    def get(self, internal_id):
        return self._db.get(internal_id)
    def update(self, internal_id, data):
        if internal_id not in self._db:
            raise Exception('Not found')
        self._db[internal_id].update(data)
        return self._db[internal_id]
    def delete(self, internal_id):
        if internal_id in self._db:
            del self._db[internal_id]
            return True
        return False

def test_customer_repository_add_success():
    repo = DummyCustomerRepository()
    customer = {'name': 'Maria'}
    customer_id = repo.add(customer)
    assert customer_id == 1

def test_customer_repository_add_failure():
    repo = DummyCustomerRepository()
    customer = {}
    with pytest.raises(Exception):
        repo.add(customer)

def test_customer_repository_get():
    repo = DummyCustomerRepository()
    customer = {'name': 'GetTest'}
    customer_id = repo.add(customer)
    result = repo.get(customer_id)
    assert result['name'] == 'GetTest'

def test_customer_repository_update():
    repo = DummyCustomerRepository()
    customer = {'name': 'ToUpdate'}
    customer_id = repo.add(customer)
    updated = repo.update(customer_id, {'name': 'Updated'})
    assert updated['name'] == 'Updated'

def test_customer_repository_delete():
    repo = DummyCustomerRepository()
    customer = {'name': 'ToDelete'}
    customer_id = repo.add(customer)
    result = repo.delete(customer_id)
    assert result is True
