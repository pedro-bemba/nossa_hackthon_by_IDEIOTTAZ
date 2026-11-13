from datetime import datetime, timezone

import requests

from app.integrations.weather.base import Observation, WeatherProvider


class OpenMeteoProvider(WeatherProvider):
    name = "open-meteo"
    BASE = "https://api.open-meteo.com/v1/forecast"

    def get_observation(self, lat: float, lon: float, day) -> Observation:
        r = requests.get(self.BASE, params={
            "latitude": lat, "longitude": lon,
            "daily": "precipitation_sum", "timezone": "Africa/Luanda",
            "start_date": day.isoformat(), "end_date": day.isoformat(),
        }, timeout=10)
        r.raise_for_status()
        mm = r.json()["daily"]["precipitation_sum"][0]
        return Observation(
            value_mm=float(mm or 0.0), date=day, lat=lat, lon=lon,
            source="open-meteo", version="v1",
            quality_score=0.9, ingested_at=datetime.now(timezone.utc),
        )