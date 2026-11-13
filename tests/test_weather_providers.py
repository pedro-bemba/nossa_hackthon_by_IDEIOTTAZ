from datetime import date, datetime, timezone
from pathlib import Path

import pytest

from app.integrations.weather.base import Observation
from app.integrations.weather.inamet import INAMETProvider

HUAMBO = (-12.77, 15.73)
DAY = date(2024, 2, 15)

HAS_CHIRPS = any(Path("data/chirps").glob("*.nc"))


def test_inamet_devolve_observation() -> None:
    obs = INAMETProvider().get_observation(*HUAMBO, DAY)
    assert obs.source == "inamet"
    assert obs.value_mm >= 0


def test_inamet_reprodutivel() -> None:
    a = INAMETProvider().get_observation(*HUAMBO, DAY)
    b = INAMETProvider().get_observation(*HUAMBO, DAY)
    assert a.value_mm == b.value_mm


def test_inamet_fora_do_raio_levanta() -> None:
    with pytest.raises(ValueError):
        INAMETProvider().get_observation(0.0, 0.0, DAY)


def test_observation_rejeita_quality_invalido() -> None:
    with pytest.raises(ValueError):
        Observation(
            value_mm=1.0, date=DAY, lat=0.0, lon=0.0,
            source="x", version="v1", quality_score=1.5,
            ingested_at=datetime.now(timezone.utc),
        )


def test_observation_rejeita_value_negativo() -> None:
    with pytest.raises(ValueError):
        Observation(
            value_mm=-1.0, date=DAY, lat=0.0, lon=0.0,
            source="x", version="v1", quality_score=0.5,
            ingested_at=datetime.now(timezone.utc),
        )


@pytest.mark.skipif(not HAS_CHIRPS, reason="CHIRPS .nc não descarregado em data/chirps/")
def test_chirps_devolve_observation() -> None:
    from app.integrations.weather.chirps import CHIRPSProvider
    obs = CHIRPSProvider().get_observation(*HUAMBO, DAY)
    assert obs.source == "chirps"