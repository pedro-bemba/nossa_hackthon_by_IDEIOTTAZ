from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_providers_lista() -> None:
    r = client.get("/weather/providers")
    assert r.status_code == 200
    body = r.json()
    assert "inamet" in body["providers"]
    assert "chirps" in body["providers"]
    assert "inamet" in body["mock_providers"]


def test_inamet_observation() -> None:
    r = client.get(
        "/weather/inamet",
        params={"lat": -12.77, "lon": 15.73, "day": "2024-02-15"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["source"] == "inamet"
    assert body["is_mock"] is True
    assert body["value_mm"] >= 0


def test_inamet_fora_do_raio_da_422() -> None:
    r = client.get("/weather/inamet", params={"lat": 0, "lon": 0})
    assert r.status_code == 422


def test_source_desconhecido_da_404() -> None:
    r = client.get("/weather/naoexiste", params={"lat": -12.77, "lon": 15.73})
    assert r.status_code == 404


def test_chirps_sem_dados_da_503() -> None:
    # Assume que data/chirps/ está vazio (estado actual)
    r = client.get(
        "/weather/chirps",
        params={"lat": -12.77, "lon": 15.73, "day": "2024-02-15"},
    )
    assert r.status_code in (200, 503)  # 200 se .nc existir


def test_lat_fora_do_intervalo_da_422() -> None:
    r = client.get("/weather/inamet", params={"lat": 100, "lon": 15.73})
    assert r.status_code == 422


def test_combined_devolve_parcial() -> None:
    r = client.get(
        "/weather/combined/all",
        params={"lat": -12.77, "lon": 15.73, "day": "2024-02-15"},
    )
    assert r.status_code == 200
    body = r.json()
    # INAMET responde; CHIRPS sem .nc → erro
    assert any(o["source"] == "inamet" for o in body["observations"])
    # Com menos de 2 observations não há divergência
    if len(body["observations"]) < 2:
        assert body["divergence"] is None


def test_health_ainda_responde() -> None:
    """Regressão: /health continua público após registar /weather."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"