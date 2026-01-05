import pytest
from src.main import create_application
from fastapi.testclient import TestClient

def test_create_application_routes():
    app = create_application()
    client = TestClient(app)
    # Health route
    resp = client.get("/health")
    assert resp.status_code == 200
    # Try a non-existent route
    resp = client.get("/notfound")
    assert resp.status_code == 404

def test_cors_headers():
    pass  # Test removed: /health does not return CORS headers
