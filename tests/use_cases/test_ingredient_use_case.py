from src.application.use_cases.ingredient_use_cases import (
    IngredientCreateUseCase, IngredientReadUseCase, IngredientUpdateUseCase, IngredientDeleteUseCase,
    IngredientListUseCase, IngredientListByTypeUseCase, IngredientListByAppliesToUseCase
)
from src.application.dto import IngredientCreateRequest, IngredientUpdateRequest
from src.entities.ingredient import IngredientType

class DummyIngredientRepository:
    def __init__(self):
        self._db = {}
        self._id = 1
    def save(self, ingredient):
        ingredient.internal_id = self._id
        self._db[self._id] = ingredient
        self._id += 1
        return ingredient
    def find_by_id(self, ingredient_internal_id, include_inactive=False):
        return self._db.get(ingredient_internal_id)
    def update(self, ingredient):
        if ingredient.internal_id in self._db:
            self._db[ingredient.internal_id] = ingredient
            return ingredient
        raise Exception('Not found')
    def delete(self, ingredient_internal_id):
        if ingredient_internal_id in self._db:
            del self._db[ingredient_internal_id]
            return True
        return False
    def find_all(self, include_inactive=False):
        return list(self._db.values())
    def find_by_ingredient_type(self, ingredient_type, include_inactive=False):
        return [i for i in self._db.values() if i.ingredient_type == ingredient_type]
    def find_by_type(self, ingredient_type, include_inactive=False):
        return self.find_by_ingredient_type(ingredient_type, include_inactive)
    def find_by_applies_usage(self, category, include_inactive=False):
        return list(self._db.values())
    def exists_by_name(self, name):
        return any(getattr(i.name, 'value', i.name) == name for i in self._db.values())

def test_ingredient_create_and_read():
    repo = DummyIngredientRepository()
    create_uc = IngredientCreateUseCase(repo)
    read_uc = IngredientReadUseCase(repo)
    req = IngredientCreateRequest(
        name='Sal', price=1.0, is_active=True, ingredient_type=IngredientType.SAUCE,
        applies_to_burger=True, applies_to_side=False, applies_to_drink=False, applies_to_dessert=False
    )
    resp = create_uc.execute(req)
    assert resp.name == 'Sal'
    resp2 = read_uc.execute(resp.internal_id)
    assert resp2.name == 'Sal'

def test_ingredient_update_and_delete():
    repo = DummyIngredientRepository()
    create_uc = IngredientCreateUseCase(repo)
    update_uc = IngredientUpdateUseCase(repo)
    delete_uc = IngredientDeleteUseCase(repo)
    req = IngredientCreateRequest(
        name='Sal', price=1.0, is_active=True, ingredient_type=IngredientType.SAUCE,
        applies_to_burger=True, applies_to_side=False, applies_to_drink=False, applies_to_dessert=False
    )
    resp = create_uc.execute(req)
    upd_req = IngredientUpdateRequest(
        internal_id=resp.internal_id, name='Sal', price=2.0, is_active=True, ingredient_type=IngredientType.SAUCE,
        applies_to_burger=True, applies_to_side=False, applies_to_drink=False, applies_to_dessert=False
    )
    resp2 = update_uc.execute(upd_req)
    assert resp2.name == 'Sal'
    assert delete_uc.execute(resp2.internal_id) is True

def test_ingredient_list_and_by_type():
    repo = DummyIngredientRepository()
    create_uc = IngredientCreateUseCase(repo)
    list_uc = IngredientListUseCase(repo)
    by_type_uc = IngredientListByTypeUseCase(repo)
    req = IngredientCreateRequest(
        name='Sal', price=1.0, is_active=True, ingredient_type=IngredientType.SAUCE,
        applies_to_burger=True, applies_to_side=False, applies_to_drink=False, applies_to_dessert=False
    )
    create_uc.execute(req)
    assert list_uc.execute().total_count == 1
    assert by_type_uc.execute(IngredientType.SAUCE).total_count == 1

def test_ingredient_list_by_applies_to():
    repo = DummyIngredientRepository()
    create_uc = IngredientCreateUseCase(repo)
    by_applies_uc = IngredientListByAppliesToUseCase(repo)
    req = IngredientCreateRequest(
        name='Sal', price=1.0, is_active=True, ingredient_type=IngredientType.SAUCE,
        applies_to_burger=True, applies_to_side=False, applies_to_drink=False, applies_to_dessert=False
    )
    create_uc.execute(req)
    assert by_applies_uc.execute('burger').total_count == 1
