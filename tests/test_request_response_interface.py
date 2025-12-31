from src.application.dto.interfaces.request_interface import RequestInterface
from src.application.dto.interfaces.response_interface import ResponseInterface

class DummyRequest(RequestInterface):
    def to_dict(self):
        return {"foo": "bar"}

class DummyResponse(ResponseInterface):
    def to_dict(self):
        return {"bar": "baz"}
    @classmethod
    def from_entity(cls, entity):
        return cls()

def test_request_interface_to_dict():
    req = DummyRequest()
    assert req.to_dict() == {"foo": "bar"}

def test_response_interface_to_dict_and_from_entity():
    resp = DummyResponse()
    assert resp.to_dict() == {"bar": "baz"}
    assert isinstance(DummyResponse.from_entity(None), DummyResponse)
