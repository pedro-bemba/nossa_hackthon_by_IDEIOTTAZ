import hashlib
import math
from dataclasses import dataclass
from datetime import datetime, timezone

from app.integrations.weather.base import Observation, WeatherProvider


@dataclass(frozen=True)
class Station:
    name: str
    province: str
    lat: float
    lon: float
    base_mm: float


STATIONS = [
    Station("Huambo",  "Huambo",  -12.77, 15.73, 1.2),
    Station("Kuito",   "Bié",     -12.39, 16.94, 1.0),
    Station("Ondjiva", "Cunene",  -17.07, 15.73, 0.4),
    Station("Malanje", "Malanje",  -9.55, 16.34, 1.5),
    Station("Lubango", "Huíla",   -14.92, 13.49, 0.8),
]

MAX_DIST_DEG = 0.5


class INAMETProvider(WeatherProvider):
    """MOCK determinístico — interface do que seria a API INAMET real.

    NÃO é uma integração real. Ver docs/SIMULATED_VS_REAL.md.
    """
    name = "inamet"

    def get_observation(self, lat: float, lon: float, day) -> Observation:
        station = min(STATIONS, key=lambda s: (s.lat - lat) ** 2 + (s.lon - lon) ** 2)
        dist = math.sqrt((station.lat - lat) ** 2 + (station.lon - lon) ** 2)
        if dist > MAX_DIST_DEG:
            raise ValueError(f"Sem estação INAMET a <{MAX_DIST_DEG}° de ({lat},{lon})")

        seed = f"{station.name}|{day.isoformat()}"
        h = int(hashlib.sha256(seed.encode()).hexdigest(), 16) % 1000
        value_mm = round(station.base_mm * (h / 100.0), 1)

        return Observation(
            value_mm=value_mm, date=day, lat=lat, lon=lon,
            source="inamet", version="mock-v1",
            quality_score=0.85, ingested_at=datetime.now(timezone.utc),
        )