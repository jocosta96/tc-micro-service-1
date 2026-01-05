import pytest
from sqlalchemy.exc import SQLAlchemyError

from src.adapters.gateways.implementations.sqlalchemy_database import SQLAlchemyDatabase


class SessionStub:
    def __init__(self, results=None, raise_on=None):
        self.results = results or []
        self.raise_on = raise_on or {}
        self.added = []
        self.merged = []
        self.deleted = []
        self.committed = False
        self.rolled_back = False
        self.flushed = False
        self.closed = False
        self.query_calls = []

    def _maybe_raise(self, method):
        if method in self.raise_on:
            raise self.raise_on[method]

    def add(self, entity):
        self._maybe_raise("add")
        self.added.append(entity)

    def merge(self, entity):
        self._maybe_raise("merge")
        self.merged.append(entity)

    def delete(self, entity):
        self._maybe_raise("delete")
        self.deleted.append(entity)

    def flush(self):
        self._maybe_raise("flush")
        self.flushed = True

    def commit(self):
        self._maybe_raise("commit")
        self.committed = True

    def rollback(self):
        self._maybe_raise("rollback")
        self.rolled_back = True

    def close(self):
        self._maybe_raise("close")
        self.closed = True

    def query(self, entity_class):
        self._maybe_raise("query")
        qs = QueryStub(self.results)
        self.query_calls.append((entity_class, qs))
        return qs


class QueryStub:
    def __init__(self, results):
        self.results = results
        self.filters = []

    def filter(self, condition):
        self.filters.append(condition)
        return self

    def first(self):
        return self.results[0] if self.results else None

    def all(self):
        return list(self.results)


class EntityStub:
    internal_id = "id"
    active = True
    name = "stub"


def make_db(monkeypatch, session):
    monkeypatch.setattr(
        "src.adapters.gateways.implementations.sqlalchemy_database.create_engine",
        lambda *_, **__: "engine",
    )
    monkeypatch.setattr(
        "src.adapters.gateways.implementations.sqlalchemy_database.sessionmaker",
        lambda **kwargs: (lambda: session),
    )
    return SQLAlchemyDatabase("sqlite://")


def test_get_session_uses_sessionmaker(monkeypatch):
    session = SessionStub()
    db = make_db(monkeypatch, session)

    assert db.get_session() is session


def test_add_success(monkeypatch):
    session = SessionStub()
    db = make_db(monkeypatch, session)
    entity = object()

    result = db.add(session, entity)

    assert result is entity
    assert session.added == [entity]
    assert session.flushed is True
    assert session.rolled_back is False


def test_add_sqlalchemy_error(monkeypatch):
    error = SQLAlchemyError("fail")
    session = SessionStub(raise_on={"add": error})
    db = make_db(monkeypatch, session)

    with pytest.raises(ValueError):
        db.add(session, object())

    assert session.rolled_back is True


def test_update_success(monkeypatch):
    session = SessionStub()
    db = make_db(monkeypatch, session)
    entity = object()

    result = db.update(session, entity)

    assert result is entity
    assert session.merged == [entity]
    assert session.flushed is True


def test_update_sqlalchemy_error(monkeypatch):
    error = SQLAlchemyError("boom")
    session = SessionStub(raise_on={"merge": error})
    db = make_db(monkeypatch, session)

    with pytest.raises(ValueError):
        db.update(session, object())

    assert session.rolled_back is True


def test_delete_success(monkeypatch):
    session = SessionStub()
    db = make_db(monkeypatch, session)
    entity = object()

    assert db.delete(session, entity) is True
    assert session.deleted == [entity]


def test_delete_sqlalchemy_error(monkeypatch):
    error = SQLAlchemyError("fail")
    session = SessionStub(raise_on={"delete": error})
    db = make_db(monkeypatch, session)

    with pytest.raises(ValueError):
        db.delete(session, object())

    assert session.rolled_back is True


def test_find_by_id_success(monkeypatch):
    entity = EntityStub()
    session = SessionStub(results=[entity])
    db = make_db(monkeypatch, session)

    result = db.find_by_id(session, EntityStub, 1)

    assert result is entity
    assert session.query_calls


def test_find_by_id_sqlalchemy_error(monkeypatch):
    error = SQLAlchemyError("fail")
    session = SessionStub(raise_on={"query": error})
    db = make_db(monkeypatch, session)

    with pytest.raises(ValueError):
        db.find_by_id(session, EntityStub, 1)


def test_find_all_success(monkeypatch):
    entities = [EntityStub(), EntityStub()]
    session = SessionStub(results=entities)
    db = make_db(monkeypatch, session)

    assert db.find_all(session, EntityStub) == entities


def test_find_by_field_success(monkeypatch):
    entity = EntityStub()
    session = SessionStub(results=[entity])
    db = make_db(monkeypatch, session)

    result = db.find_by_field(session, EntityStub, "name", "stub")

    assert result is entity


def test_find_by_field_invalid_field(monkeypatch):
    session = SessionStub()
    db = make_db(monkeypatch, session)

    with pytest.raises(ValueError):
        db.find_by_field(session, EntityStub, "missing", "value")


def test_find_all_by_field_success(monkeypatch):
    entity = EntityStub()
    session = SessionStub(results=[entity])
    db = make_db(monkeypatch, session)

    results = db.find_all_by_field(session, EntityStub, "name", "stub")

    assert results == [entity]


def test_find_all_by_field_invalid(monkeypatch):
    session = SessionStub()
    db = make_db(monkeypatch, session)

    with pytest.raises(ValueError):
        db.find_all_by_field(session, EntityStub, "invalid", "value")


def test_find_all_by_boolean_field_success(monkeypatch):
    entity = EntityStub()
    session = SessionStub(results=[entity])
    db = make_db(monkeypatch, session)

    results = db.find_all_by_boolean_field(session, EntityStub, "active", True)

    assert results == [entity]


def test_find_all_by_boolean_field_invalid(monkeypatch):
    session = SessionStub()
    db = make_db(monkeypatch, session)

    with pytest.raises(ValueError):
        db.find_all_by_boolean_field(session, EntityStub, "invalid", True)


def test_find_all_by_multiple_fields_success(monkeypatch):
    entity = EntityStub()
    session = SessionStub(results=[entity])
    db = make_db(monkeypatch, session)

    results = db.find_all_by_multiple_fields(
        session, EntityStub, {"name": "stub", "active": True}
    )

    assert results == [entity]
    assert len(session.query_calls[0][1].filters) == 2


def test_find_all_by_multiple_fields_invalid(monkeypatch):
    session = SessionStub()
    db = make_db(monkeypatch, session)

    with pytest.raises(ValueError):
        db.find_all_by_multiple_fields(session, EntityStub, {"missing": "x"})


def test_exists_by_field_true(monkeypatch):
    entity = EntityStub()
    session = SessionStub(results=[entity])
    db = make_db(monkeypatch, session)

    assert db.exists_by_field(session, EntityStub, "name", "stub") is True


def test_exists_by_field_false(monkeypatch):
    session = SessionStub(results=[])
    db = make_db(monkeypatch, session)

    assert db.exists_by_field(session, EntityStub, "name", "stub") is False


def test_exists_by_field_invalid(monkeypatch):
    session = SessionStub()
    db = make_db(monkeypatch, session)

    with pytest.raises(ValueError):
        db.exists_by_field(session, EntityStub, "invalid", "value")


def test_commit_success(monkeypatch):
    session = SessionStub()
    db = make_db(monkeypatch, session)

    db.commit(session)

    assert session.committed is True
    assert session.rolled_back is False


def test_commit_sqlalchemy_error(monkeypatch):
    error = SQLAlchemyError("fail")
    session = SessionStub(raise_on={"commit": error})
    db = make_db(monkeypatch, session)

    with pytest.raises(ValueError):
        db.commit(session)

    assert session.rolled_back is True


def test_rollback_success(monkeypatch):
    session = SessionStub()
    db = make_db(monkeypatch, session)

    db.rollback(session)

    assert session.rolled_back is True


def test_rollback_sqlalchemy_error(monkeypatch):
    error = SQLAlchemyError("oops")
    session = SessionStub(raise_on={"rollback": error})
    db = make_db(monkeypatch, session)

    with pytest.raises(ValueError):
        db.rollback(session)


def test_close_session_success(monkeypatch):
    session = SessionStub()
    db = make_db(monkeypatch, session)

    db.close_session(session)

    assert session.closed is True


def test_close_session_sqlalchemy_error(monkeypatch):
    error = SQLAlchemyError("close fail")
    session = SessionStub(raise_on={"close": error})
    db = make_db(monkeypatch, session)

    with pytest.raises(ValueError):
        db.close_session(session)
