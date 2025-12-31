from src.adapters.presenters.interfaces.presenter_interface import PresenterInterface

class DummyPresenter(PresenterInterface):
    def present(self, data):
        return {"data": data}
    def present_list(self, data_list):
        return {"data": data_list}
    def present_error(self, error):
        return {"error": str(error)}

def test_presenter_interface_methods():
    presenter = DummyPresenter()
    assert presenter.present(1) == {"data": 1}
    assert presenter.present_list([1,2]) == {"data": [1,2]}
    assert presenter.present_error(Exception("fail")) == {"error": "fail"}
