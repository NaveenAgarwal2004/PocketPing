"""
Tests for health.py — Flask health endpoints.

Uses Flask test client directly; no network or thread involved.
"""

import pytest
from health import health_app


@pytest.fixture
def client():
    health_app.config["TESTING"] = True
    with health_app.test_client() as c:
        yield c


class TestHealthEndpoints:
    def test_root_status_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_root_body(self, client):
        response = client.get("/")
        assert response.data == b"Bot is running"

    def test_health_status_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_body(self, client):
        response = client.get("/health")
        assert response.data == b"OK"

    def test_unknown_route_404(self, client):
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_post_to_root_405(self, client):
        """Health endpoints are GET-only."""
        response = client.post("/")
        assert response.status_code == 405
