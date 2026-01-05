import os

import pytest
from botocore.exceptions import ClientError, EndpointConnectionError, NoCredentialsError

from src.config import aws_ssm
from src.config.aws_ssm import SSMParameterStore, clear_aws_credentials


class StubSSMClient:
    def __init__(self):
        self.calls = {}
        self.parameters = {}
        self.invalid_parameters = []
        self.raise_on = {}

    def get_parameter(self, **kwargs):
        self.calls.setdefault("get_parameter", []).append(kwargs)
        if "get_parameter" in self.raise_on:
            raise self.raise_on["get_parameter"]
        return {"Parameter": {"Value": self.parameters.get(kwargs["Name"], "")}}

    def get_parameters(self, **kwargs):
        self.calls.setdefault("get_parameters", []).append(kwargs)
        if "get_parameters" in self.raise_on:
            raise self.raise_on["get_parameters"]
        names = kwargs["Names"]
        params = [{"Name": name, "Value": self.parameters.get(name, "")} for name in names if name in self.parameters]
        return {"Parameters": params, "InvalidParameters": [n for n in names if n not in self.parameters] if self.invalid_parameters is None else self.invalid_parameters}

    def describe_parameters(self, **kwargs):
        self.calls.setdefault("describe_parameters", []).append(kwargs)
        if "describe_parameters" in self.raise_on:
            raise self.raise_on["describe_parameters"]
        return {"Parameters": []}


@pytest.fixture(autouse=True)
def reset_globals():
    aws_ssm._ssm_client = None
    clear_aws_credentials()
    yield
    aws_ssm._ssm_client = None
    clear_aws_credentials()


def test_create_client_prefers_global_credentials(monkeypatch):
    aws_ssm._aws_credentials.update(
        {
            "aws_access_key_id": "id",
            "aws_secret_access_key": "secret",
            "aws_session_token": "token",
        }
    )
    captured = {}

    def fake_client(service, **kwargs):
        captured["kwargs"] = kwargs
        return StubSSMClient()

    monkeypatch.setattr(aws_ssm, "boto3", type("B", (), {"client": staticmethod(fake_client)}))

    client = SSMParameterStore(region_name="sa-east-1")

    assert isinstance(client.ssm_client, StubSSMClient)
    assert captured["kwargs"]["aws_access_key_id"] == "id"
    assert captured["kwargs"]["region_name"] == "sa-east-1"


def test_create_client_uses_env(monkeypatch):
    clear_aws_credentials()
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "env-id")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "env-secret")
    called = {}

    def fake_client(service, **kwargs):
        called["region_name"] = kwargs["region_name"]
        return StubSSMClient()

    monkeypatch.setattr(aws_ssm, "boto3", type("B", (), {"client": staticmethod(fake_client)}))

    client = SSMParameterStore(region_name=None)

    assert called["region_name"] == os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    assert isinstance(client.ssm_client, StubSSMClient)


def test_create_client_defaults(monkeypatch):
    clear_aws_credentials()
    monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)
    called = {}

    def fake_client(service, **kwargs):
        called["region_name"] = kwargs["region_name"]
        return StubSSMClient()

    monkeypatch.setattr(aws_ssm, "boto3", type("B", (), {"client": staticmethod(fake_client)}))

    client = SSMParameterStore(region_name="us-east-2")

    assert called["region_name"] == "us-east-2"
    assert isinstance(client.ssm_client, StubSSMClient)


def test_update_credentials_recreates_client(monkeypatch):
    stub = StubSSMClient()

    def fake_client(service, **kwargs):
        return stub

    monkeypatch.setattr(aws_ssm, "boto3", type("B", (), {"client": staticmethod(fake_client)}))
    client = SSMParameterStore(region_name="eu-west-1")

    client.update_credentials("new", "secret", "token")

    assert client.ssm_client is stub
    assert aws_ssm._aws_credentials["aws_access_key_id"] == "new"


def test_get_parameter_success(monkeypatch):
    stub = StubSSMClient()
    stub.parameters["/param"] = "value"
    monkeypatch.setattr(aws_ssm, "boto3", type("B", (), {"client": staticmethod(lambda *_, **__: stub)}))
    client = SSMParameterStore(region_name="us-east-1")

    result = client.get_parameter("/param")

    assert result == "value"
    assert stub.calls["get_parameter"][0]["WithDecryption"] is True


def test_get_parameter_not_found(monkeypatch):
    error = ClientError({"Error": {"Code": "ParameterNotFound"}}, "GetParameter")
    stub = StubSSMClient()
    stub.raise_on["get_parameter"] = error
    monkeypatch.setattr(aws_ssm, "boto3", type("B", (), {"client": staticmethod(lambda *_, **__: stub)}))
    client = SSMParameterStore(region_name="us-east-1")

    assert client.get_parameter("/missing") is None


def test_get_parameter_other_client_error(monkeypatch):
    error = ClientError({"Error": {"Code": "AccessDenied"}}, "GetParameter")
    stub = StubSSMClient()
    stub.raise_on["get_parameter"] = error
    monkeypatch.setattr(aws_ssm, "boto3", type("B", (), {"client": staticmethod(lambda *_, **__: stub)}))
    client = SSMParameterStore(region_name="us-east-1")

    with pytest.raises(ClientError):
        client.get_parameter("/deny")


def test_get_parameter_no_credentials(monkeypatch):
    stub = StubSSMClient()
    stub.raise_on["get_parameter"] = NoCredentialsError()
    monkeypatch.setattr(aws_ssm, "boto3", type("B", (), {"client": staticmethod(lambda *_, **__: stub)}))
    client = SSMParameterStore(region_name="us-east-1")

    with pytest.raises(NoCredentialsError):
        client.get_parameter("/nocreds")


def test_get_parameters_empty_list(monkeypatch):
    monkeypatch.setattr(aws_ssm, "boto3", type("B", (), {"client": staticmethod(lambda *_, **__: StubSSMClient())}))
    client = SSMParameterStore(region_name="us-east-1")
    assert client.get_parameters([]) == {}


def test_get_parameters_batches(monkeypatch):
    stub = StubSSMClient()
    stub.parameters = {f"/p{i}": f"v{i}" for i in range(12)}
    monkeypatch.setattr(aws_ssm, "boto3", type("B", (), {"client": staticmethod(lambda *_, **__: stub)}))
    client = SSMParameterStore(region_name="us-east-1")

    names = [f"/p{i}" for i in range(12)]
    result = client.get_parameters(names, decrypt=False)

    assert result["/p0"] == "v0"
    assert result["/p11"] == "v11"
    # Should have made two batch calls
    assert len(stub.calls["get_parameters"]) == 2


def test_get_parameters_error(monkeypatch):
    stub = StubSSMClient()
    stub.raise_on["get_parameters"] = EndpointConnectionError(endpoint_url="x")
    monkeypatch.setattr(aws_ssm, "boto3", type("B", (), {"client": staticmethod(lambda *_, **__: stub)}))
    client = SSMParameterStore(region_name="us-east-1")

    with pytest.raises(EndpointConnectionError):
        client.get_parameters(["/a"])


def test_get_parameter_with_fallback_found(monkeypatch):
    stub = StubSSMClient()
    stub.parameters["/exists"] = "val"
    monkeypatch.setattr(aws_ssm, "boto3", type("B", (), {"client": staticmethod(lambda *_, **__: stub)}))
    client = SSMParameterStore(region_name="us-east-1")

    assert client.get_parameter_with_fallback("/exists", "fallback") == "val"


def test_get_parameter_with_fallback_missing(monkeypatch):
    stub = StubSSMClient()
    stub.raise_on["get_parameter"] = ClientError({"Error": {"Code": "ParameterNotFound"}}, "GetParameter")
    monkeypatch.setattr(aws_ssm, "boto3", type("B", (), {"client": staticmethod(lambda *_, **__: stub)}))
    client = SSMParameterStore(region_name="us-east-1")

    assert client.get_parameter_with_fallback("/missing", "fallback") == "fallback"


def test_get_parameter_with_fallback_on_error(monkeypatch):
    stub = StubSSMClient()
    stub.raise_on["get_parameter"] = NoCredentialsError()
    monkeypatch.setattr(aws_ssm, "boto3", type("B", (), {"client": staticmethod(lambda *_, **__: stub)}))
    client = SSMParameterStore(region_name="us-east-1")

    assert client.get_parameter_with_fallback("/err", "fallback") == "fallback"


def test_health_check_success(monkeypatch):
    stub = StubSSMClient()
    monkeypatch.setattr(aws_ssm, "boto3", type("B", (), {"client": staticmethod(lambda *_, **__: stub)}))
    client = SSMParameterStore(region_name="us-east-1")

    assert client.health_check() is True


def test_health_check_failure(monkeypatch):
    stub = StubSSMClient()
    stub.raise_on["describe_parameters"] = Exception("fail")
    monkeypatch.setattr(aws_ssm, "boto3", type("B", (), {"client": staticmethod(lambda *_, **__: stub)}))
    client = SSMParameterStore(region_name="us-east-1")

    assert client.health_check() is False


def test_set_aws_credentials_updates_client(monkeypatch):
    tracker = {}

    class Client(SSMParameterStore):
        def update_credentials(self, access, secret, token=None):
            tracker["called"] = (access, secret, token)

    monkeypatch.setattr(aws_ssm, "boto3", type("B", (), {"client": staticmethod(lambda *_, **__: StubSSMClient())}))
    aws_ssm._ssm_client = Client(region_name="us-east-1")
    result = aws_ssm.set_aws_credentials("id", "secret", "token")

    assert result is True
    assert tracker["called"] == ("id", "secret", "token")
    status = aws_ssm.get_aws_credentials_status()
    assert status["credentials_set"] is True


def test_set_aws_credentials_failure(monkeypatch):
    class BadClient(SSMParameterStore):
        def update_credentials(self, *_, **__):
            raise RuntimeError("fail")

    monkeypatch.setattr(aws_ssm, "boto3", type("B", (), {"client": staticmethod(lambda *_, **__: StubSSMClient())}))
    aws_ssm._ssm_client = BadClient(region_name="us-east-1")
    result = aws_ssm.set_aws_credentials("id", "secret", "token")

    assert result is False


def test_clear_and_status():
    aws_ssm.set_aws_credentials("id", "secret", None)
    clear_aws_credentials()
    status = aws_ssm.get_aws_credentials_status()
    assert status["credentials_set"] is False
    assert status["has_access_key"] is False
    assert status["has_secret_key"] is False


def test_get_ssm_client_singleton(monkeypatch):
    stub = StubSSMClient()
    monkeypatch.setattr(aws_ssm, "boto3", type("B", (), {"client": staticmethod(lambda *_, **__: stub)}))

    client1 = aws_ssm.get_ssm_client()
    client2 = aws_ssm.get_ssm_client()

    assert client1 is client2
    assert isinstance(client1, SSMParameterStore)
