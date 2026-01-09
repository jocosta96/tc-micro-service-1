from src.adapters.presenters.implementations.json_presenter import JSONPresenter
from src.application.exceptions import CustomerNotFoundException

def test_present_error_status_code():
    presenter = JSONPresenter()
    error = CustomerNotFoundException("not found")
    result = presenter.present_error(error)
    assert "error" in result
    assert "status_code" in result["error"]
    assert result["error"]["status_code"] == 404

def test_present_list_empty():
    presenter = JSONPresenter()
    result = presenter.present_list([])
    assert isinstance(result, dict)
    assert "data" in result
    assert result["data"] == []

def test_present_generic():
    presenter = JSONPresenter()
    result = presenter._present_generic({"foo": "bar"})
    assert "foo" in result["data"]
