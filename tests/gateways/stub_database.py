from typing import Any, Dict, List, Optional

from src.adapters.gateways.interfaces.database_interface import DatabaseInterface


class _FakeSession:
    """Minimal session object to satisfy the DatabaseInterface contract in tests."""

    def __init__(self, store: Dict[type, List[Any]]):
        self.store = store
        self.closed = False


class InMemoryDatabase(DatabaseInterface):
    """In-memory stub for DatabaseInterface used to isolate gateway tests."""

    def __init__(self):
        self.store: Dict[type, List[Any]] = {}
        self.committed = False
        self.rolled_back = False
        self.fail_commit = False
        self.fail_add = False
        self.fail_update = False

    def get_session(self) -> _FakeSession:
        return _FakeSession(self.store)

    def add(self, session: _FakeSession, entity: Any) -> Any:
        if self.fail_add:
            raise ValueError("add failed")
        table = session.store.setdefault(type(entity), [])
        if getattr(entity, "internal_id", None) is None:
            entity.internal_id = len(table) + 1
        table.append(entity)
        return entity

    def update(self, session: _FakeSession, entity: Any) -> Any:
        if self.fail_update:
            raise ValueError("update failed")
        table = session.store.setdefault(type(entity), [])
        for idx, current in enumerate(table):
            if getattr(current, "internal_id", None) == getattr(entity, "internal_id", None):
                table[idx] = entity
                return entity
        table.append(entity)
        return entity

    def delete(self, session: _FakeSession, entity: Any) -> bool:
        table = session.store.setdefault(type(entity), [])
        for idx, current in enumerate(table):
            if getattr(current, "internal_id", None) == getattr(entity, "internal_id", None):
                table.pop(idx)
                return True
        return False

    def find_by_id(self, session: _FakeSession, entity_class: type, entity_id: int) -> Optional[Any]:
        return self.find_by_field(session, entity_class, "internal_id", entity_id)

    def find_all(self, session: _FakeSession, entity_class: type) -> List[Any]:
        return list(session.store.get(entity_class, []))

    def find_by_field(
        self, session: _FakeSession, entity_class: type, field_name: str, field_value: Any
    ) -> Optional[Any]:
        for item in session.store.get(entity_class, []):
            if getattr(item, field_name, None) == field_value:
                return item
        return None

    def find_all_by_field(
        self, session: _FakeSession, entity_class: type, field_name: str, field_value: Any
    ) -> List[Any]:
        return [
            item
            for item in session.store.get(entity_class, [])
            if getattr(item, field_name, None) == field_value
        ]

    def find_all_by_boolean_field(
        self, session: _FakeSession, entity_class: type, field_name: str, field_value: bool
    ) -> List[Any]:
        return [
            item
            for item in session.store.get(entity_class, [])
            if bool(getattr(item, field_name, None)) is field_value
        ]

    def find_all_by_multiple_fields(
        self, session: _FakeSession, entity_class: type, field_values: Dict[str, Any]
    ) -> List[Any]:
        results: List[Any] = []
        for item in session.store.get(entity_class, []):
            if all(getattr(item, field) == value for field, value in field_values.items()):
                results.append(item)
        return results

    def exists_by_field(
        self, session: _FakeSession, entity_class: type, field_name: str, field_value: Any
    ) -> bool:
        return self.find_by_field(session, entity_class, field_name, field_value) is not None

    def commit(self, session: _FakeSession) -> None:
        if self.fail_commit:
            raise ValueError("commit failed")
        self.committed = True

    def rollback(self, session: _FakeSession) -> None:
        self.rolled_back = True
        self.committed = False

    def close_session(self, session: _FakeSession) -> None:
        session.closed = True
