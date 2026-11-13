from datetime import date

from app.core.config import get_settings
from app.integrations.weather.base import Observation, WeatherProvider
from app.integrations.weather.chirps import CHIRPSProvider
from app.integrations.weather.inamet import INAMETProvider
from app.integrations.weather.open_meteo import OpenMeteoProvider


_REGISTRY: dict[str, type[WeatherProvider]] = {
    "chirps": CHIRPSProvider,
    "inamet": INAMETProvider,
    "open-meteo": OpenMeteoProvider,
}


def get_provider(name: str | None = None) -> WeatherProvider:
    name = name or getattr(get_settings(), "weather_provider", "chirps")
    if name not in _REGISTRY:
        raise ValueError(f"Provider desconhecido: {name}. Disponíveis: {list(_REGISTRY)}")
    return _REGISTRY[name]()


def get_combined_observations(lat: float, lon: float, day: date) -> list[Observation]:
    """Consulta INAMET + CHIRPS; ignora falhas individuais."""
    results: list[Observation] = []
    for name in ("inamet", "chirps"):
        try:
            results.append(get_provider(name).get_observation(lat, lon, day))
        except (FileNotFoundError, ValueError):
            continue
    return results

# Providers que devolvem dados simulados — declarado aqui para a camada HTTP
# poder marcar `is_mock` sem inferir pela string do source.
MOCK_SOURCES: frozenset[str] = frozenset({"inamet"})


def list_providers() -> list[str]:
    return sorted(_REGISTRY.keys())