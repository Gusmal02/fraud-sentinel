"""Tests de la API."""
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "checks" in data


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["sistema"] == "Fraud Sentinel"


def test_analyze_claim_requires_minimum_text():
    response = client.post("/analyze-claim", json={"texto": "corto"})
    assert response.status_code == 422  # Pydantic validation error


def test_analyze_claim_accepts_valid_text():
    texto = "Siniestro de prueba para testing automatizado. " * 5
    response = client.post("/analyze-claim", json={"texto": texto})
    assert response.status_code == 200
    assert "status" in response.json()