import pytest
from src.application.use_cases.ingredient_use_cases import (
    IngredientCreateUseCase, IngredientReadUseCase, IngredientUpdateUseCase, IngredientDeleteUseCase,
    IngredientListUseCase, IngredientListByTypeUseCase, IngredientListByAppliesToUseCase
)
from src.application.dto import IngredientCreateRequest, IngredientUpdateRequest
from src.application.exceptions import (
    IngredientNotFoundException,
    IngredientAlreadyExistsException
)
from src.entities.ingredient import IngredientType
from src.entities.product import ProductCategory

class DummyIngredientRepository:
    def __init__(self):
        self._db = {}
        self._id = 1
        self._existing_names = set()

    def save(self, ingredient):
        if ingredient.internal_id is None:
            ingredient.internal_id = self._id
            self._db[self._id] = ingredient
            self._id += 1
        else:
            self._db[ingredient.internal_id] = ingredient

        self._existing_names.add(ingredient.name.value)
        return ingredient

    def find_by_id(self, ingredient_internal_id, include_inactive=False):
        ingredient = self._db.get(ingredient_internal_id)
        if ingredient and (include_inactive or ingredient.is_active):
            return ingredient
        return None

    def find_all(self, include_inactive=False):
        if include_inactive:
            return list(self._db.values())
        return [i for i in self._db.values() if i.is_active]

    def find_by_ingredient_type(self, ingredient_type, include_inactive=False):
        ingredients = [i for i in self._db.values() if i.ingredient_type == ingredient_type]
        if not include_inactive:
            ingredients = [i for i in ingredients if i.is_active]
        return ingredients

    def find_by_applies_usage(self, category, include_inactive=False):
        # Mapeia categoria para campo applies_to_*
        field_map = {
            ProductCategory.BURGER: 'applies_to_burger',
            ProductCategory.SIDE: 'applies_to_side',
            ProductCategory.DRINK: 'applies_to_drink',
            ProductCategory.DESSERT: 'applies_to_dessert',
        }
        field_name = field_map.get(category)
        if not field_name:
            return []

        ingredients = [i for i in self._db.values() if getattr(i, field_name, False)]
        if not include_inactive:
            ingredients = [i for i in ingredients if i.is_active]
        return ingredients

    def exists_by_name(self, name, include_inactive=False):
        return name in self._existing_names

    def delete(self, ingredient_internal_id):
        if ingredient_internal_id in self._db:
            self._db[ingredient_internal_id].is_active = False
            return True
        return False

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
    assert by_applies_uc.execute(ProductCategory.BURGER).total_count == 1


# ===== FASE 2: Testes de cenários de erro e validações =====

# IngredientCreateUseCase - cenários de erro
def test_create_ingredient_name_already_exists():
    """Given nome já existe, When execute, Then IngredientAlreadyExistsException"""
    repo = DummyIngredientRepository()
    use_case = IngredientCreateUseCase(repo)

    # Cria primeiro ingrediente
    req1 = IngredientCreateRequest(
        name='Queijo Cheddar',
        price=2.5,
        is_active=True,
        ingredient_type=IngredientType.CHEESE,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False
    )
    use_case.execute(req1)

    # Tenta criar segundo com mesmo nome
    req2 = IngredientCreateRequest(
        name='Queijo Cheddar',
        price=3.0,
        is_active=True,
        ingredient_type=IngredientType.CHEESE,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False
    )
    with pytest.raises(IngredientAlreadyExistsException) as exc_info:
        use_case.execute(req2)
    assert 'Queijo Cheddar' in str(exc_info.value)


def test_create_ingredient_invalid_price():
    """Given preço inválido (Money), When execute, Then ValueError"""
    repo = DummyIngredientRepository()
    use_case = IngredientCreateUseCase(repo)

    req = IngredientCreateRequest(
        name='Ingrediente Inválido',
        price=-5.0,  # Preço negativo
        is_active=True,
        ingredient_type=IngredientType.SAUCE,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False
    )
    with pytest.raises(ValueError):
        use_case.execute(req)


# IngredientUpdateUseCase - cenários de erro
def test_update_ingredient_not_found():
    """Given id inexistente, When execute, Then IngredientNotFoundException"""
    repo = DummyIngredientRepository()
    use_case = IngredientUpdateUseCase(repo)

    req = IngredientUpdateRequest(
        internal_id=999,
        name='Not Found',
        price=1.0,
        is_active=True,
        ingredient_type=IngredientType.SAUCE,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False
    )
    with pytest.raises(IngredientNotFoundException) as exc_info:
        use_case.execute(req)
    assert '999' in str(exc_info.value)


def test_update_ingredient_name_change_to_existing():
    """Given troca de nome para existente, When execute, Then IngredientAlreadyExistsException"""
    repo = DummyIngredientRepository()
    create_uc = IngredientCreateUseCase(repo)
    update_uc = IngredientUpdateUseCase(repo)

    # Cria dois ingredientes
    ingredient1 = create_uc.execute(IngredientCreateRequest(
        name='Alface',
        price=1.0,
        is_active=True,
        ingredient_type=IngredientType.SALAD,
        applies_to_burger=True,
        applies_to_side=True,
        applies_to_drink=False,
        applies_to_dessert=False
    ))

    ingredient2 = create_uc.execute(IngredientCreateRequest(
        name='Tomate',
        price=1.5,
        is_active=True,
        ingredient_type=IngredientType.SALAD,
        applies_to_burger=True,
        applies_to_side=True,
        applies_to_drink=False,
        applies_to_dessert=False
    ))

    # Tenta atualizar ingredient2 com nome de ingredient1
    update_req = IngredientUpdateRequest(
        internal_id=ingredient2.internal_id,
        name='Alface',  # nome de ingredient1
        price=1.5,
        is_active=True,
        ingredient_type=IngredientType.SALAD,
        applies_to_burger=True,
        applies_to_side=True,
        applies_to_drink=False,
        applies_to_dessert=False
    )
    with pytest.raises(IngredientAlreadyExistsException) as exc_info:
        update_uc.execute(update_req)
    assert ingredient1.name in str(exc_info.value)


def test_update_ingredient_same_name_same_id_success():
    """Given atualiza com mesmo nome mas mesmo ID, When execute, Then sucesso"""
    repo = DummyIngredientRepository()
    create_uc = IngredientCreateUseCase(repo)
    update_uc = IngredientUpdateUseCase(repo)

    ingredient = create_uc.execute(IngredientCreateRequest(
        name='Picles',
        price=1.0,
        is_active=True,
        ingredient_type=IngredientType.SALAD,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False
    ))

    # Atualiza preço mas mantém nome
    update_req = IngredientUpdateRequest(
        internal_id=ingredient.internal_id,
        name='Picles',  # mesmo nome
        price=1.5,  # preço diferente
        is_active=True,
        ingredient_type=IngredientType.SALAD,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False
    )
    result = update_uc.execute(update_req)
    assert result.name == 'Picles'
    assert result.price == 1.5


# IngredientDeleteUseCase - cenários de erro
def test_delete_ingredient_not_found():
    """Given ingrediente inexistente, When execute, Then IngredientNotFoundException"""
    repo = DummyIngredientRepository()
    use_case = IngredientDeleteUseCase(repo)

    with pytest.raises(IngredientNotFoundException) as exc_info:
        use_case.execute(999)
    assert '999' in str(exc_info.value)


def test_delete_ingredient_success():
    """Given ingrediente existe, When execute, Then soft delete e retorna True"""
    repo = DummyIngredientRepository()
    create_uc = IngredientCreateUseCase(repo)
    delete_uc = IngredientDeleteUseCase(repo)

    ingredient = create_uc.execute(IngredientCreateRequest(
        name='To Delete',
        price=1.0,
        is_active=True,
        ingredient_type=IngredientType.SAUCE,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False
    ))

    result = delete_uc.execute(ingredient.internal_id)
    assert result is True


# IngredientListByAppliesToUseCase - cenários
def test_list_by_applies_to_burger():
    """Given categoria burger, When execute, Then repo.find_by_applies_usage chamado com ProductCategory.BURGER"""
    repo = DummyIngredientRepository()
    create_uc = IngredientCreateUseCase(repo)
    list_by_applies_uc = IngredientListByAppliesToUseCase(repo)

    # Cria ingredientes com diferentes applies_to
    create_uc.execute(IngredientCreateRequest(
        name='Pão',
        price=1.0,
        is_active=True,
        ingredient_type=IngredientType.BREAD,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False
    ))

    create_uc.execute(IngredientCreateRequest(
        name='Batata',
        price=2.0,
        is_active=True,
        ingredient_type=IngredientType.SALAD,
        applies_to_burger=False,
        applies_to_side=True,
        applies_to_drink=False,
        applies_to_dessert=False
    ))

    result = list_by_applies_uc.execute(ProductCategory.BURGER)
    assert result.total_count == 1
    assert result.ingredients[0].name == 'Pão'


def test_list_by_applies_to_include_inactive():
    """Given include_inactive True, When execute, Then passa flag corretamente"""
    repo = DummyIngredientRepository()
    create_uc = IngredientCreateUseCase(repo)
    list_by_applies_uc = IngredientListByAppliesToUseCase(repo)

    # Cria ingrediente ativo
    create_uc.execute(IngredientCreateRequest(
        name='Ativo',
        price=1.0,
        is_active=True,
        ingredient_type=IngredientType.SAUCE,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False
    ))

    # Cria ingrediente inativo
    inactive_ingredient = create_uc.execute(IngredientCreateRequest(
        name='Inativo',
        price=1.0,
        is_active=True,
        ingredient_type=IngredientType.SAUCE,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False
    ))
    # Deleta para tornar inativo
    delete_uc = IngredientDeleteUseCase(repo)
    delete_uc.execute(inactive_ingredient.internal_id)

    # Sem include_inactive, deve retornar apenas 1
    result_active_only = list_by_applies_uc.execute(ProductCategory.BURGER, include_inactive=False)
    assert result_active_only.total_count == 1

    # Com include_inactive, deve retornar 2
    result_all = list_by_applies_uc.execute(ProductCategory.BURGER, include_inactive=True)
    assert result_all.total_count == 2
