from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health_db_responde_ok() -> None:
    resposta = client.get("/health/db")
    assert resposta.status_code == 200
    assert resposta.json()["database"] == "connected"

def test_swagger_disponivel() -> None:
    assert client.get("/docs").status_code == 200

