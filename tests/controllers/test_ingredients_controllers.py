import pytest
from src.adapters.controllers.ingredient_controller import IngredientController
from src.adapters.presenters.implementations.json_presenter import JSONPresenter
from src.entities.ingredient import Ingredient
from src.entities.value_objects.name import Name
from src.application.dto.implementation.ingredient_dto import IngredientCreateRequest, IngredientUpdateRequest


# Dummy repository for Ingredient
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
    def exists_by_name(self, name, include_inactive=False):
        return False


# Fixture for controller and repo
@pytest.fixture(scope='module')
def controller():
    repo = DummyIngredientRepository()
    presenter = JSONPresenter()
    return IngredientController(repo, presenter), repo

def test_create_ingredient(controller):
    ctrl, repo = controller
    payload = {
        'name': 'Sal',
        'price': 1.0,
        'is_active': True,
        'ingredient_type': 'bread',
        'applies_to_burger': True,
        'applies_to_side': False,
        'applies_to_drink': False,
        'applies_to_dessert': False
    }
    response = ctrl.create_ingredient(payload)
    assert response['name'] == 'Sal'
    assert response['ingredient_type'] == 'bread'
    assert response['price'] == 1.0

def test_get_ingredient(controller):
    ctrl, repo = controller
    payload = {
        'name': 'Açúcar',
        'price': 2.0,
        'is_active': True,
        'ingredient_type': 'bread',
        'applies_to_burger': True,
        'applies_to_side': False,
        'applies_to_drink': False,
        'applies_to_dessert': False
    }
    from src.entities.value_objects.money import Money
    from src.entities.value_objects.name import Name
    from src.entities.ingredient import Ingredient, IngredientType
    ingredient = repo.save(Ingredient.create(
        name=payload['name'],
        price=Money(amount=payload['price']),
        is_active=payload['is_active'],
        ingredient_type=IngredientType(payload['ingredient_type']),
        applies_to_burger=payload['applies_to_burger'],
        applies_to_side=payload['applies_to_side'],
        applies_to_drink=payload['applies_to_drink'],
        applies_to_dessert=payload['applies_to_dessert']
    ))
    response = ctrl.get_ingredient(ingredient.internal_id)
    assert response['name'] == 'Açúcar'
    assert response['ingredient_type'] == 'bread'
    assert response['price'] == 2.0

def test_update_ingredient(controller):
    ctrl, repo = controller
    payload = {
        'name': 'Pimenta',
        'price': 3.0,
        'is_active': True,
        'ingredient_type': 'bread',
        'applies_to_burger': True,
        'applies_to_side': False,
        'applies_to_drink': False,
        'applies_to_dessert': False
    }
    from src.entities.value_objects.money import Money
    from src.entities.value_objects.name import Name
    from src.entities.ingredient import Ingredient, IngredientType
    ingredient = repo.save(Ingredient.create(
        name=payload['name'],
        price=Money(amount=payload['price']),
        is_active=payload['is_active'],
        ingredient_type=IngredientType(payload['ingredient_type']),
        applies_to_burger=payload['applies_to_burger'],
        applies_to_side=payload['applies_to_side'],
        applies_to_drink=payload['applies_to_drink'],
        applies_to_dessert=payload['applies_to_dessert']
    ))
    update_payload = {
        'internal_id': ingredient.internal_id,
        'name': 'Pimenta-do-reino',
        'price': 3.5,
        'is_active': True,
        'ingredient_type': 'bread',
        'applies_to_burger': True,
        'applies_to_side': False,
        'applies_to_drink': False,
        'applies_to_dessert': False
    }
    response = ctrl.update_ingredient(update_payload)
    # Accept both 'Pimenta-do-reino' and 'Pimenta-Do-Reino' (title case)
    assert response['name'].lower() == 'pimenta-do-reino'
    assert response['price'] == 3.5

def test_delete_ingredient(controller):
    ctrl, repo = controller
    payload = {
        'name': 'Orégano',
        'price': 0.5,
        'is_active': True,
        'ingredient_type': 'bread',
        'applies_to_burger': True,
        'applies_to_side': False,
        'applies_to_drink': False,
        'applies_to_dessert': False
    }
    from src.entities.value_objects.money import Money
    from src.entities.value_objects.name import Name
    from src.entities.ingredient import Ingredient, IngredientType
    ingredient = repo.save(Ingredient.create(
        name=payload['name'],
        price=Money(amount=payload['price']),
        is_active=payload['is_active'],
        ingredient_type=IngredientType(payload['ingredient_type']),
        applies_to_burger=payload['applies_to_burger'],
        applies_to_side=payload['applies_to_side'],
        applies_to_drink=payload['applies_to_drink'],
        applies_to_dessert=payload['applies_to_dessert']
    ))
    result = ctrl.delete_ingredient(ingredient.internal_id)
    # Accept presenter dict output or True
    if isinstance(result, dict) and 'data' in result and 'success' in str(result['data']).lower():
        assert 'success' in str(result['data']).lower()
    else:
        assert result is True
