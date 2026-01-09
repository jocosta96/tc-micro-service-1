import pytest
from src.application.use_cases.product_use_cases import (
    ProductCreateUseCase, ProductReadUseCase, ProductUpdateUseCase, ProductDeleteUseCase,
    ProductListUseCase, ProductListByCategoryUseCase
)
from src.application.dto.implementation.product_dto import ProductCreateRequest, ProductUpdateRequest
from src.application.exceptions import (
    ProductNotFoundException,
    ProductAlreadyExistsException,
    ProductValidationException
)

from src.entities.product import ProductCategory, ProductReceiptItem
from src.entities.ingredient import Ingredient, IngredientType
from src.entities.value_objects.name import Name
from src.entities.value_objects.money import Money

class DummyProductRepository:
    def __init__(self):
        self._db = {}
        self._id = 1
        self._existing_skus = set()

    def save(self, product):
        if product.internal_id is None:
            product.internal_id = self._id
            self._db[self._id] = product
            self._id += 1
        else:
            self._db[product.internal_id] = product

        self._existing_skus.add(str(product.sku))
        return product

    def find_by_id(self, product_internal_id, include_inactive=False):
        product = self._db.get(product_internal_id)
        if product and (include_inactive or product.is_active):
            return product
        return None

    def find_by_sku(self, sku, include_inactive=False):
        sku_str = str(sku)
        for product in self._db.values():
            if str(product.sku) == sku_str:
                if include_inactive or product.is_active:
                    return product
        return None

    def exists_by_sku(self, sku):
        return str(sku) in self._existing_skus

    def find_all(self, include_inactive=False):
        if include_inactive:
            return list(self._db.values())
        return [p for p in self._db.values() if p.is_active]

    def delete(self, product_internal_id):
        if product_internal_id in self._db:
            self._db[product_internal_id].is_active = False
            return True
        return False

def test_product_create_and_read():
    repo = DummyProductRepository()
    create_uc = ProductCreateUseCase(repo)
    read_uc = ProductReadUseCase(repo)
    dummy_ingredient = Ingredient(
        name=Name('Dummy'),
        price=Money(1.0),
        is_active=True,
        ingredient_type=IngredientType.BREAD,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False,
        internal_id=1
    )
    default_ingredient = [ProductReceiptItem(dummy_ingredient, 1)]
    req = ProductCreateRequest(
        name='Produto', price=1.0, sku='SKU-1234-ABC', category=ProductCategory.BURGER, default_ingredient=default_ingredient
    )
    resp = create_uc.execute(req)
    assert resp.name == 'Produto'
    resp2 = read_uc.execute(resp.internal_id)
    assert resp2.name == 'Produto'

def test_product_update_and_delete():
    repo = DummyProductRepository()
    create_uc = ProductCreateUseCase(repo)
    update_uc = ProductUpdateUseCase(repo)
    delete_uc = ProductDeleteUseCase(repo)
    dummy_ingredient = Ingredient(
        name=Name('Dummy'),
        price=Money(1.0),
        is_active=True,
        ingredient_type=IngredientType.BREAD,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False,
        internal_id=1
    )
    default_ingredient = [ProductReceiptItem(dummy_ingredient, 1)]
    req = ProductCreateRequest(
        name='Produto', price=1.0, sku='SKU-1234-ABC', category=ProductCategory.BURGER, default_ingredient=default_ingredient
    )
    resp = create_uc.execute(req)
    upd_req = ProductUpdateRequest(
        internal_id=resp.internal_id, name='Produto Novo', price=2.0, sku='SKU-1234-ABC', category=ProductCategory.BURGER, default_ingredient=default_ingredient
    )
    resp2 = update_uc.execute(upd_req)
    assert resp2.name == 'Produto Novo'
    assert delete_uc.execute(resp2.internal_id) is True

def test_product_list_and_by_category():
    repo = DummyProductRepository()
    create_uc = ProductCreateUseCase(repo)
    list_uc = ProductListUseCase(repo)
    by_cat_uc = ProductListByCategoryUseCase(repo)
    dummy_ingredient = Ingredient(
        name=Name('Dummy'),
        price=Money(1.0),
        is_active=True,
        ingredient_type=IngredientType.BREAD,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False,
        internal_id=1
    )
    default_ingredient = [ProductReceiptItem(dummy_ingredient, 1)]
    req = ProductCreateRequest(
        name='Produto', price=1.0, sku='SKU-1234-ABC', category=ProductCategory.BURGER, default_ingredient=default_ingredient
    )
    create_uc.execute(req)
    assert list_uc.execute().total_count == 1
    assert by_cat_uc.execute(ProductCategory.BURGER).total_count == 1


# ===== FASE 2: Testes de cenários de erro e validações =====

def _create_dummy_ingredient(category=ProductCategory.BURGER):
    """Helper para criar ingrediente dummy para testes"""
    if category == ProductCategory.BURGER:
        return Ingredient(
            name=Name('Test Burger Ingredient'),
            price=Money(1.0),
            is_active=True,
            ingredient_type=IngredientType.BREAD,
            applies_to_burger=True,
            applies_to_side=False,
            applies_to_drink=False,
            applies_to_dessert=False,
            internal_id=1
        )
    elif category == ProductCategory.SIDE:
        return Ingredient(
            name=Name('Test Side Ingredient'),
            price=Money(1.0),
            is_active=True,
            ingredient_type=IngredientType.SALAD,
            applies_to_burger=False,
            applies_to_side=True,
            applies_to_drink=False,
            applies_to_dessert=False,
            internal_id=2
        )
    elif category == ProductCategory.DRINK:
        return Ingredient(
            name=Name('Test Drink Ingredient'),
            price=Money(1.0),
            is_active=True,
            ingredient_type=IngredientType.SAUCE,
            applies_to_burger=False,
            applies_to_side=False,
            applies_to_drink=True,
            applies_to_dessert=False,
            internal_id=3
        )
    else:  # DESSERT
        return Ingredient(
            name=Name('Test Dessert Ingredient'),
            price=Money(1.0),
            is_active=True,
            ingredient_type=IngredientType.SAUCE,
            applies_to_burger=False,
            applies_to_side=False,
            applies_to_drink=False,
            applies_to_dessert=True,
            internal_id=4
        )


# ProductCreateUseCase - cenários de erro
def test_create_product_sku_already_exists():
    """Given SKU já existe, When execute, Then ProductAlreadyExistsException"""
    repo = DummyProductRepository()
    use_case = ProductCreateUseCase(repo)

    # Cria primeiro produto
    req1 = ProductCreateRequest(
        name='First Product',
        price=10.0,
        sku='SKU-1234-ABC',
        category=ProductCategory.BURGER,
        default_ingredient=[ProductReceiptItem(_create_dummy_ingredient(ProductCategory.BURGER), 1)]
    )
    use_case.execute(req1)

    # Tenta criar segundo produto com mesmo SKU (mas categoria diferente)
    req2 = ProductCreateRequest(
        name='Second Product',
        price=15.0,
        sku='SKU-1234-ABC',
        category=ProductCategory.SIDE,
        default_ingredient=[ProductReceiptItem(_create_dummy_ingredient(ProductCategory.SIDE), 1)]
    )
    with pytest.raises(ProductAlreadyExistsException) as exc_info:
        use_case.execute(req2)
    assert 'SKU-1234-ABC' in str(exc_info.value)


# ProductUpdateUseCase - cenários de erro
def test_update_product_not_found():
    """Given id inexistente, When execute, Then ProductNotFoundException"""
    repo = DummyProductRepository()
    use_case = ProductUpdateUseCase(repo)

    req = ProductUpdateRequest(
        internal_id=999,
        name='Not Found',
        price=10.0,
        sku='SKU-1234-XYZ',
        category=ProductCategory.BURGER,
        default_ingredient=[ProductReceiptItem(_create_dummy_ingredient(ProductCategory.BURGER), 1)]
    )
    with pytest.raises(ProductNotFoundException) as exc_info:
        use_case.execute(req)
    assert '999' in str(exc_info.value)


def test_update_product_sku_belongs_to_another():
    """Given SKU pertence a outro produto, When execute, Then ProductAlreadyExistsException"""
    repo = DummyProductRepository()
    create_uc = ProductCreateUseCase(repo)
    update_uc = ProductUpdateUseCase(repo)

    # Cria dois produtos
    product1 = create_uc.execute(ProductCreateRequest(
        name='Product One',
        price=10.0,
        sku='SKU-1111-AAA',
        category=ProductCategory.BURGER,
        default_ingredient=[ProductReceiptItem(_create_dummy_ingredient(ProductCategory.BURGER), 1)]
    ))

    product2 = create_uc.execute(ProductCreateRequest(
        name='Product Two',
        price=15.0,
        sku='SKU-2222-BBB',
        category=ProductCategory.SIDE,
        default_ingredient=[ProductReceiptItem(_create_dummy_ingredient(ProductCategory.SIDE), 1)]
    ))

    # Tenta atualizar product2 com SKU de product1
    update_req = ProductUpdateRequest(
        internal_id=product2.internal_id,
        name='Product Two Updated',
        price=15.0,
        sku='SKU-1111-AAA',  # SKU de product1
        category=ProductCategory.SIDE,
        default_ingredient=[ProductReceiptItem(_create_dummy_ingredient(ProductCategory.SIDE), 1)]
    )
    with pytest.raises(ProductAlreadyExistsException) as exc_info:
        update_uc.execute(update_req)
    assert product1.sku in str(exc_info.value)


# ProductDeleteUseCase - cenários de erro
def test_delete_product_not_found():
    """Given produto inexistente, When execute, Then ProductNotFoundException"""
    repo = DummyProductRepository()
    use_case = ProductDeleteUseCase(repo)

    with pytest.raises(ProductNotFoundException) as exc_info:
        use_case.execute(999)
    assert '999' in str(exc_info.value)


def test_delete_product_success():
    """Given produto existe, When execute, Then delete chamado e retorna True"""
    repo = DummyProductRepository()
    create_uc = ProductCreateUseCase(repo)
    delete_uc = ProductDeleteUseCase(repo)

    product = create_uc.execute(ProductCreateRequest(
        name='To Delete',
        price=10.0,
        sku='SKU-9999-ZZZ',
        category=ProductCategory.BURGER,
        default_ingredient=[ProductReceiptItem(_create_dummy_ingredient(ProductCategory.BURGER), 1)]
    ))

    result = delete_uc.execute(product.internal_id)
    assert result is True


# ProductListByCategoryUseCase - cenários
def test_list_by_category_invalid_category():
    """Given categoria inválida, When execute, Then ProductValidationException"""
    repo = DummyProductRepository()
    use_case = ProductListByCategoryUseCase(repo)

    with pytest.raises(ProductValidationException) as exc_info:
        use_case.execute('INVALID_CATEGORY')
    assert 'Invalid category' in str(exc_info.value)


def test_list_by_category_filters_correctly():
    """Given produtos com categorias variadas, When execute com category, Then retorna apenas filtrados"""
    repo = DummyProductRepository()
    create_uc = ProductCreateUseCase(repo)
    list_by_cat_uc = ProductListByCategoryUseCase(repo)

    # Cria ingredientes para diferentes categorias
    burger_ingredient = Ingredient(
        name=Name('Burger Ingredient'),
        price=Money(1.0),
        is_active=True,
        ingredient_type=IngredientType.BREAD,
        applies_to_burger=True,
        applies_to_side=False,
        applies_to_drink=False,
        applies_to_dessert=False,
        internal_id=1
    )

    side_ingredient = Ingredient(
        name=Name('Side Ingredient'),
        price=Money(1.0),
        is_active=True,
        ingredient_type=IngredientType.SALAD,
        applies_to_burger=False,
        applies_to_side=True,
        applies_to_drink=False,
        applies_to_dessert=False,
        internal_id=2
    )

    # Cria produtos de diferentes categorias
    create_uc.execute(ProductCreateRequest(
        name='Classic Burger',
        price=10.0,
        sku='BRG-0001-AAA',
        category=ProductCategory.BURGER,
        default_ingredient=[ProductReceiptItem(burger_ingredient, 1)]
    ))

    create_uc.execute(ProductCreateRequest(
        name='Cheese Burger',
        price=12.0,
        sku='BRG-0002-BBB',
        category=ProductCategory.BURGER,
        default_ingredient=[ProductReceiptItem(burger_ingredient, 1)]
    ))

    create_uc.execute(ProductCreateRequest(
        name='French Fries',
        price=5.0,
        sku='SID-0001-AAA',
        category=ProductCategory.SIDE,
        default_ingredient=[ProductReceiptItem(side_ingredient, 1)]
    ))

    # Lista apenas burgers
    burger_result = list_by_cat_uc.execute(ProductCategory.BURGER)
    assert burger_result.total_count == 2

    # Lista apenas sides
    side_result = list_by_cat_uc.execute(ProductCategory.SIDE)
    assert side_result.total_count == 1
