import pytest
from src.application.use_cases.customer_use_cases import (
    CustomerCreateUseCase,
    CustomerReadUseCase,
    CustomerUpdateUseCase,
    CustomerDeleteUseCase,
    CustomerGetAnonymousUseCase
)
from src.application.dto.implementation.customer_dto import CustomerCreateRequest, CustomerUpdateRequest
from src.application.exceptions import (
    CustomerNotFoundException,
    CustomerAlreadyExistsException,
    CustomerBusinessRuleException
)
from src.entities.customer import Customer

class DummyCustomerRepository:
    def __init__(self):
        self._db = {}
        self._id = 1
        self._exists_documents = set()
        self._exists_emails = set()

    def save(self, customer):
        if customer.internal_id is None:
            customer.internal_id = self._id
            self._db[self._id] = customer
            self._id += 1
        else:
            self._db[customer.internal_id] = customer

        if not customer.document.is_empty:
            self._exists_documents.add(customer.document.value)
        if customer.email.value:
            self._exists_emails.add(customer.email.value)

        return customer

    def find_by_id(self, customer_internal_id, include_inactive=False):
        customer = self._db.get(customer_internal_id)
        if customer and (include_inactive or customer.is_active):
            return customer
        return None

    def find_by_document(self, document, include_inactive=False):
        for customer in self._db.values():
            if not customer.document.is_empty and customer.document.value == document:
                if include_inactive or customer.is_active:
                    return customer
        return None

    def find_by_email(self, email, include_inactive=False):
        for customer in self._db.values():
            if customer.email.value == email:
                if include_inactive or customer.is_active:
                    return customer
        return None

    def exists_by_document(self, document, include_inactive=False):
        return document in self._exists_documents

    def exists_by_email(self, email, include_inactive=False):
        return email in self._exists_emails

    def delete(self, customer_internal_id):
        if customer_internal_id in self._db:
            customer = self._db[customer_internal_id]
            customer.is_active = False
            return True
        return False

    def get_anonymous_customer(self):
        # Retorna um customer anônimo pré-criado ou cria um novo
        for customer in self._db.values():
            if customer.is_anonymous:
                return customer
        # Cria um novo cliente anônimo
        anonymous = Customer.create_anonymous()
        return self.save(anonymous)

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


# ===== FASE 2: Testes de cenários de erro e validações =====

# CustomerCreateUseCase - cenários de erro
def test_create_customer_document_already_exists():
    """Given document já existe no repo, When execute, Then CustomerAlreadyExistsException"""
    repo = DummyCustomerRepository()
    use_case = CustomerCreateUseCase(repo)

    # Cria primeiro cliente
    data1 = CustomerCreateRequest(
        first_name='First',
        last_name='Customer',
        email='first@example.com',
        document='52998224725'
    )
    use_case.execute(data1)

    # Tenta criar segundo com mesmo documento
    data2 = CustomerCreateRequest(
        first_name='Second',
        last_name='Customer',
        email='second@example.com',
        document='52998224725'
    )
    with pytest.raises(CustomerAlreadyExistsException) as exc_info:
        use_case.execute(data2)
    assert '52998224725' in str(exc_info.value)


def test_create_customer_email_already_exists():
    """Given email já existe, When execute, Then CustomerAlreadyExistsException"""
    repo = DummyCustomerRepository()
    use_case = CustomerCreateUseCase(repo)

    # Cria primeiro cliente
    data1 = CustomerCreateRequest(
        first_name='First',
        last_name='Customer',
        email='duplicate@example.com',
        document='52998224725'
    )
    use_case.execute(data1)

    # Tenta criar segundo com mesmo email
    data2 = CustomerCreateRequest(
        first_name='Second',
        last_name='Customer',
        email='duplicate@example.com',
        document='39053344705'
    )
    with pytest.raises(CustomerAlreadyExistsException) as exc_info:
        use_case.execute(data2)
    assert 'duplicate@example.com' in str(exc_info.value)


def test_create_customer_cannot_place_order():
    """Given cliente não atende can_place_order, When execute, Then CustomerBusinessRuleException"""
    repo = DummyCustomerRepository()
    use_case = CustomerCreateUseCase(repo)

    # Cliente sem email e sem document não pode fazer pedidos (a menos que seja anônimo)
    data = CustomerCreateRequest(
        first_name='No',
        last_name='Order',
        email='no-order@example.com',
        document=''
    )
    with pytest.raises(CustomerBusinessRuleException) as exc_info:
        use_case.execute(data)
    assert 'requirements to place orders' in str(exc_info.value)


# CustomerUpdateUseCase - cenários de erro
def test_update_customer_not_found():
    """Given id inexistente, When execute, Then CustomerNotFoundException"""
    repo = DummyCustomerRepository()
    use_case = CustomerUpdateUseCase(repo)

    data = CustomerUpdateRequest(
        internal_id=999,
        first_name='Not',
        last_name='Found',
        email='notfound@example.com',
        document='52998224725'
    )
    with pytest.raises(CustomerNotFoundException) as exc_info:
        use_case.execute(data)
    assert '999' in str(exc_info.value)


def test_update_customer_document_belongs_to_another():
    """Given novo document pertence a outro cliente, When execute, Then CustomerAlreadyExistsException"""
    repo = DummyCustomerRepository()
    create_use_case = CustomerCreateUseCase(repo)
    update_use_case = CustomerUpdateUseCase(repo)

    # Cria dois clientes
    customer1 = create_use_case.execute(CustomerCreateRequest(
        first_name='Customer',
        last_name='One',
        email='one@example.com',
        document='52998224725'
    ))

    customer2 = create_use_case.execute(CustomerCreateRequest(
        first_name='Customer',
        last_name='Two',
        email='two@example.com',
        document='39053344705'
    ))

    # Tenta atualizar customer2 com documento de customer1
    update_data = CustomerUpdateRequest(
        internal_id=customer2.internal_id,
        first_name='Customer',
        last_name='Two',
        email='two@example.com',
        document='52998224725'  # documento de customer1
    )
    with pytest.raises(CustomerAlreadyExistsException) as exc_info:
        update_use_case.execute(update_data)
    assert '52998224725' in str(exc_info.value)


def test_update_customer_email_belongs_to_another():
    """Given novo email pertence a outro cliente, When execute, Then CustomerAlreadyExistsException"""
    repo = DummyCustomerRepository()
    create_use_case = CustomerCreateUseCase(repo)
    update_use_case = CustomerUpdateUseCase(repo)

    # Cria dois clientes
    customer1 = create_use_case.execute(CustomerCreateRequest(
        first_name='Customer',
        last_name='One',
        email='one@example.com',
        document='52998224725'
    ))

    customer2 = create_use_case.execute(CustomerCreateRequest(
        first_name='Customer',
        last_name='Two',
        email='two@example.com',
        document='39053344705'
    ))

    # Tenta atualizar customer2 com email de customer1
    update_data = CustomerUpdateRequest(
        internal_id=customer2.internal_id,
        first_name='Customer',
        last_name='Two',
        email='one@example.com',  # email de customer1
        document='39053344705'
    )
    with pytest.raises(CustomerAlreadyExistsException) as exc_info:
        update_use_case.execute(update_data)
    assert 'one@example.com' in str(exc_info.value)


def test_update_customer_cannot_place_order():
    """Given dados válidos mas não atende can_place_order, When execute, Then CustomerBusinessRuleException"""
    repo = DummyCustomerRepository()
    create_use_case = CustomerCreateUseCase(repo)
    update_use_case = CustomerUpdateUseCase(repo)

    # Cria cliente válido
    customer = create_use_case.execute(CustomerCreateRequest(
        first_name='Valid',
        last_name='Customer',
        email='valid@example.com',
        document='52998224725'
    ))

    # Tenta atualizar removendo document (mantém email mas não pode fazer pedidos sem document)
    update_data = CustomerUpdateRequest(
        internal_id=customer.internal_id,
        first_name='Invalid',
        last_name='Customer',
        email='valid@example.com',
        document=''  # Remove document
    )
    with pytest.raises(CustomerBusinessRuleException):
        update_use_case.execute(update_data)


# CustomerDeleteUseCase - cenários de erro
def test_delete_customer_not_found():
    """Given repo.delete retorna False, When execute, Then CustomerNotFoundException"""
    repo = DummyCustomerRepository()
    use_case = CustomerDeleteUseCase(repo)

    with pytest.raises(CustomerNotFoundException) as exc_info:
        use_case.execute(999)
    assert '999' in str(exc_info.value)


# CustomerGetAnonymousUseCase - cenários
def test_get_anonymous_customer_success():
    """Given repo retorna customer anônimo, When execute, Then response com is_anonymous True"""
    repo = DummyCustomerRepository()
    use_case = CustomerGetAnonymousUseCase(repo)

    result = use_case.execute()

    assert result is not None
    assert result.is_anonymous is True


def test_get_anonymous_customer_idempotent():
    """Given múltiplas chamadas, When execute, Then retorna mesmo customer anônimo"""
    repo = DummyCustomerRepository()
    use_case = CustomerGetAnonymousUseCase(repo)

    result1 = use_case.execute()
    result2 = use_case.execute()

    # Deve retornar o mesmo ID
    assert result1.internal_id == result2.internal_id
