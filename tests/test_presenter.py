from src.adapters.presenters.implementations.json_presenter import JSONPresenter
from src.application.dto.implementation.customer_dto import CustomerResponse, CustomerListResponse
from src.application.dto.implementation.ingredient_dto import IngredientResponse, IngredientListResponse
from src.application.dto.implementation.product_dto import ProductResponse, ProductListResponse
from src.application.exceptions import CustomerNotFoundException, CustomerAlreadyExistsException, CustomerValidationException
from http import HTTPStatus

class Dummy:
    def to_dict(self):
        return {'foo': 'bar'}
    def __dict__(self):
        return {'foo': 'bar'}

presenter = JSONPresenter()

def test_present_single_data():
    d = Dummy()
    result = presenter.present(d)
    assert result['foo'] == 'bar'

def test_present_list_empty():
    result = presenter.present_list([])
    assert result['data'] == []
    assert result['total_count'] == 0

def test_present_list_with_data():
    d = Dummy()
    result = presenter.present_list([d, d])
    assert result['total_count'] == 2

def test_present_error_status_codes():
    assert presenter.present_error(CustomerValidationException('err'))['error']['status_code'] == HTTPStatus.BAD_REQUEST
    assert presenter.present_error(CustomerNotFoundException('err'))['error']['status_code'] == HTTPStatus.NOT_FOUND
    assert presenter.present_error(CustomerAlreadyExistsException('err'))['error']['status_code'] == HTTPStatus.CONFLICT
    assert presenter.present_error(Exception('err'))['error']['status_code'] == HTTPStatus.INTERNAL_SERVER_ERROR

def test_presenter_timestamp():
    d = Dummy()
    result = presenter.present(d)
    assert 'timestamp' not in result or isinstance(result.get('timestamp', ''), str)

def test_present_generic_dict_fallback():
    class NoDict:
        pass
    result = presenter._present_generic(NoDict())
    assert isinstance(result, dict)
    # Accepts either __dict__ fallback or string fallback
    assert 'data' in result or result == {}
