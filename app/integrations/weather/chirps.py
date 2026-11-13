from datetime import datetime, timezone
from pathlib import Path

import rioxarray

from app.integrations.weather.base import Observation, WeatherProvider


class CHIRPSProvider(WeatherProvider):
    name = "chirps"

    def __init__(self, data_dir: str = "data/chirps"):
        self.data_dir = Path(data_dir)

    def get_observation(self, lat: float, lon: float, day) -> Observation:
        path = self.data_dir / f"chirps-v2.0.{day.year}.days_p05.nc"
        if not path.exists():
            raise FileNotFoundError(f"CHIRPS não descarregado: {path}")

        da = rioxarray.open_rasterio(path, masked=True)
        lat_name = "latitude" if "latitude" in da.dims else "y"
        lon_name = "longitude" if "longitude" in da.dims else "x"

        selected = da.sel({lat_name: lat, lon_name: lon}, method="nearest", tolerance=0.05)
        if "time" in selected.dims:
            selected = selected.sel(time=day.isoformat(), method="nearest")

        value = float(selected.squeeze().values)
        if value != value:  # NaN = nodata na célula
            value = 0.0

        return Observation(
            value_mm=value, date=day, lat=lat, lon=lon,
            source="chirps", version="v2.0",
            quality_score=1.0, ingested_at=datetime.now(timezone.utc),
        )