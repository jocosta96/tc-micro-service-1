import pytest
from src.application.use_cases.customer_use_cases import CustomerCreateUseCase, CustomerReadUseCase, CustomerUpdateUseCase, CustomerDeleteUseCase
from src.application.dto.implementation.customer_dto import CustomerCreateRequest, CustomerUpdateRequest

class DummyCustomerRepository:
    def find_by_document(self, document, include_inactive=False):
        # Simula busca por documento, retorna None para não conflitar
        return None
    def __init__(self):
        self._db = {}
        self._id = 1
    def save(self, customer):
        customer.internal_id = self._id
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
    def find_by_email(self, email, include_inactive=False):
        # Simula busca por email, retorna None para não conflitar
        return None

def test_create_customer_use_case_success():
    repo = DummyCustomerRepository()
    use_case = CustomerCreateUseCase(repo)
    data = CustomerCreateRequest(
        first_name='Jane',
        last_name='Doe',
        email='jane.doe@example.com',
        document='52998224725'
    )
    result = use_case.execute(data)
    assert result.internal_id == 1
    assert result.first_name == 'Jane'
    assert result.last_name == 'Doe'
    assert result.email == 'jane.doe@example.com'

def test_create_customer_use_case_invalid():
    repo = DummyCustomerRepository()
    use_case = CustomerCreateUseCase(repo)
    data = CustomerCreateRequest(
        first_name='',
        last_name='',
        email='',
        document=''
    )
    with pytest.raises(Exception):
        use_case.execute(data)

def test_read_customer_use_case():
    repo = DummyCustomerRepository()
    create = CustomerCreateUseCase(repo)
    read = CustomerReadUseCase(repo)
    data = CustomerCreateRequest(
        first_name='Read',
        last_name='Test',
        email='read@example.com',
        document='52998224725'
    )
    created = create.execute(data)
    result = read.execute(created.internal_id)
    assert result.first_name == 'Read'
    assert result.last_name == 'Test'
    assert result.email == 'read@example.com'

def test_update_customer_use_case():
    repo = DummyCustomerRepository()
    create = CustomerCreateUseCase(repo)
    update = CustomerUpdateUseCase(repo)
    data = CustomerCreateRequest(
        first_name='To',
        last_name='Update',
        email='update@example.com',
        document='52998224725'
    )
    created = create.execute(data)
    update_data = CustomerUpdateRequest(
        internal_id=created.internal_id,
        first_name='Updated',
        last_name='Name',
        email='updated@example.com',
        document='52998224725'
    )
    result = update.execute(update_data)
    assert result.first_name == 'Updated'
    assert result.last_name == 'Name'
    assert result.email == 'updated@example.com'

def test_delete_customer_use_case():
    repo = DummyCustomerRepository()
    create = CustomerCreateUseCase(repo)
    delete = CustomerDeleteUseCase(repo)
    data = CustomerCreateRequest(
        first_name='To',
        last_name='Delete',
        email='delete@example.com',
        document='52998224725'
    )
    created = create.execute(data)
    result = delete.execute(created.internal_id)
    assert result is True
