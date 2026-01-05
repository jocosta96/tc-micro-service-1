from fastapi.testclient import TestClient

from src.adapters.di.container import container
from src.adapters.routes import health_routes
from src.main import app


def _client():
    return TestClient(app)


def test_health_check():
    response = _client().get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_database_health_check_handles_errors(monkeypatch):
    class FailingRepo:
        def get_anonymous_customer(self):
            raise RuntimeError("db down")

    monkeypatch.setattr(container, "_customer_repository", FailingRepo())

    response = _client().get("/health/db")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "unhealthy"
    assert "db down" in payload["error"]


def test_configuration_health_check_includes_ssm_details(monkeypatch):
    monkeypatch.setattr(
        health_routes.db_config,
        "health_check",
        lambda: {"ssm_enabled": True, "ssm_available": True, "configuration_source": "ssm_parameter_store"},
    )
    monkeypatch.setattr(
        health_routes.db_config,
        "get_ssm_parameters",
        lambda: {"host": "/ssm/host"},
    )
    monkeypatch.setattr(health_routes.db_config, "database", "testdb")

    response = _client().get("/health/config")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["configuration"]["ssm_enabled"] is True
    assert payload["configuration"]["ssm_parameters"]["host"] == "/ssm/host"


def test_reload_configuration_failure_returns_failed_status(monkeypatch):
    monkeypatch.setattr(health_routes.db_config, "reload_from_ssm", lambda: False)

    response = _client().post("/health/config/reload")

    assert response.status_code == 200
    assert response.json()["status"] == "failed"


def test_set_aws_credentials_endpoint_handles_exception(monkeypatch):
    monkeypatch.setattr(health_routes, "set_aws_credentials", lambda *args, **kwargs: (_ for _ in ()).throw(Exception("boom")))

    response = _client().post(
        "/health/aws-credentials",
        json={
            "aws_access_key_id": "id",
            "aws_secret_access_key": "secret",
            "aws_session_token": "token",
        },
    )

    assert response.status_code == 500
    assert "Error setting AWS credentials" in response.json()["detail"]


def test_clear_aws_credentials_endpoint_returns_success(monkeypatch):
    called = {"cleared": False}
    monkeypatch.setattr(health_routes, "clear_aws_credentials", lambda: called.update({"cleared": True}))
    monkeypatch.setattr(health_routes, "get_aws_credentials_status", lambda: {"credentials_set": False})

    response = _client().delete("/health/aws-credentials")

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert called["cleared"] is True
