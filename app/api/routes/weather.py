from datetime import date, datetime

import requests
from fastapi import APIRouter, HTTPException, Query

from app.integrations.weather.base import Observation
from app.schemas.weather import (
    CombinedResponse,
    ObservationResponse,
    ProvidersListResponse,
)
from app.services.weather_service import (
    MOCK_SOURCES,
    get_provider,
    list_providers,
)

router = APIRouter(prefix="/weather", tags=["weather"])


def _to_response(obs: Observation) -> ObservationResponse:
    return ObservationResponse(
        value_mm=obs.value_mm,
        date=obs.date,
        lat=obs.lat,
        lon=obs.lon,
        source=obs.source,
        version=obs.version,
        quality_score=obs.quality_score,
        ingested_at=obs.ingested_at,
        is_mock=obs.source in MOCK_SOURCES,
    )


def _handle_provider_error(source: str, exc: Exception) -> None:
    """Traduz excepções do provider em HTTPException semânticas."""
    if isinstance(exc, FileNotFoundError):
        raise HTTPException(
            status_code=503,
            detail=f"Fonte '{source}' indisponível: {exc}",
        ) from exc
    if isinstance(exc, ValueError):
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if isinstance(exc, requests.RequestException):
        raise HTTPException(
            status_code=502,
            detail=f"Fonte '{source}' inacessível: {exc}",
        ) from exc
    raise exc


@router.get("/providers", response_model=ProvidersListResponse)
def get_providers() -> ProvidersListResponse:
    all_providers = list_providers()
    return ProvidersListResponse(
        providers=all_providers,
        mock_providers=[p for p in all_providers if p in MOCK_SOURCES],
    )


@router.get("/{source}", response_model=ObservationResponse)
def get_observation(
    source: str,
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    day: date = Query(default_factory=date.today),
) -> ObservationResponse:
    try:
        provider = get_provider(source)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    try:
        obs = provider.get_observation(lat, lon, day)
    except Exception as exc:
        _handle_provider_error(source, exc)

    return _to_response(obs)


@router.get("/combined/all", response_model=CombinedResponse)
def get_combined(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    day: date = Query(default_factory=date.today),
) -> CombinedResponse:
    """Consulta todos os providers. Falhas individuais vão em `errors`."""
    observations: list[Observation] = []
    errors: dict[str, str] = {}

    for name in list_providers():
        if name == "open-meteo":
            continue  # forecast, não observação — não entra no gate
        try:
            observations.append(get_provider(name).get_observation(lat, lon, day))
        except Exception as exc:  # noqa: BLE001 — queremos capturar tudo
            errors[name] = f"{type(exc).__name__}: {exc}"

    divergence = _max_pairwise_divergence([o.value_mm for o in observations])

    return CombinedResponse(
        observations=[_to_response(o) for o in observations],
        errors=errors,
        divergence=divergence,
    )


def _max_pairwise_divergence(values: list[float]) -> float | None:
    """Divergência máxima entre pares, normalizada pela média. None se <2 valores."""
    if len(values) < 2:
        return None
    max_div = 0.0
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            a, b = values[i], values[j]
            mean = (a + b) / 2
            if mean == 0:
                continue
            max_div = max(max_div, abs(a - b) / mean)
    return round(max_div, 4)