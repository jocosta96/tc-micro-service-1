import pytest

from src.adapters.gateways.sql_customer_repository import CustomerModel, SQLCustomerRepository
from src.entities.customer import Customer
from src.entities.value_objects.name import Name
from tests.gateways.stub_database import InMemoryDatabase


def test_save_new_customer_assigns_id_and_commits():
    db = InMemoryDatabase()
    repo = SQLCustomerRepository(db)

    customer = Customer.create_registered(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        document="52998224725",
    )

    saved = repo.save(customer)

    assert saved.internal_id == 1
    assert db.committed is True
    assert saved.first_name.value == "John"
    assert saved.last_name.value == "Doe"


def test_save_existing_customer_updates_record():
    db = InMemoryDatabase()
    repo = SQLCustomerRepository(db)

    initial = Customer.create_registered(
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        document="52998224725",
    )
    saved = repo.save(initial)

    saved.first_name = Name.create("Janet")
    updated = repo.save(saved)

    assert updated.first_name.value == "Janet"
    assert updated.internal_id == saved.internal_id
    # Only one record stored and it was replaced
    assert len(db.store[CustomerModel]) == 1


def test_save_allows_inactive_optional_fields():
    db = InMemoryDatabase()
    repo = SQLCustomerRepository(db)

    inactive_customer = Customer.create_registered(
        first_name="Ghost",
        last_name="User",
        email="",
        document="",
        is_active=False,
    )

    saved = repo.save(inactive_customer)

    assert saved.is_active is False
    found = repo.find_by_id(saved.internal_id, include_inactive=True)
    assert found is not None
    assert found.email.value == ""
    assert found.document.is_empty


def test_save_rolls_back_on_commit_error():
    db = InMemoryDatabase()
    db.fail_commit = True
    repo = SQLCustomerRepository(db)

    customer = Customer.create_registered(
        first_name="Test",
        last_name="User",
        email="test@example.com",
        document="52998224725",
    )

    with pytest.raises(ValueError):
        repo.save(customer)

    assert db.rolled_back is True
    assert db.committed is False


def test_delete_existing_customer_soft_deletes_and_commits():
    db = InMemoryDatabase()
    repo = SQLCustomerRepository(db)

    customer = Customer.create_registered(
        first_name="To",
        last_name="Delete",
        email="delete@example.com",
        document="52998224725",
    )
    saved = repo.save(customer)

    result = repo.delete(saved.internal_id)

    assert result is True
    assert db.committed is True
    soft_deleted = repo.find_by_id(saved.internal_id, include_inactive=True)
    assert soft_deleted is not None
    assert soft_deleted.is_active is False
    assert soft_deleted.email.value.startswith("deleted.")


def test_delete_non_existing_customer_returns_false_without_commit():
    db = InMemoryDatabase()
    repo = SQLCustomerRepository(db)

    result = repo.delete(999)

    assert result is False
    assert db.committed is False
    assert db.rolled_back is False


def test_get_anonymous_customer_created_once_and_reused():
    db = InMemoryDatabase()
    repo = SQLCustomerRepository(db)

    first = repo.get_anonymous_customer()
    second = repo.get_anonymous_customer()

    assert first.is_anonymous is True
    assert second.is_anonymous is True
    assert first.internal_id == second.internal_id
    assert db.committed is True


def test_find_and_exists_respect_inactive_flag():
    db = InMemoryDatabase()
    repo = SQLCustomerRepository(db)

    active = Customer.create_registered(
        first_name="Active",
        last_name="User",
        email="active@example.com",
        document="52998224725",
    )
    inactive = Customer.create_registered(
        first_name="Inactive",
        last_name="User",
        email="inactive@example.com",
        document="39053344705",
        is_active=False,
    )
    repo.save(active)
    repo.save(inactive)

    assert repo.find_by_document(inactive.document.value) is None
    assert repo.find_by_document(inactive.document.value, include_inactive=True) is not None
    assert repo.exists_by_email(inactive.email.value) is False
    assert repo.exists_by_email(inactive.email.value, include_inactive=True) is True
    assert len(repo.find_all()) == 1
    assert len(repo.find_all(include_inactive=True)) == 2
