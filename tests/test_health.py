from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_responde_ok() -> None:
    resposta = client.get("/health")
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "ok"


def test_swagger_disponivel() -> None:
    assert client.get("/docs").status_code == 200