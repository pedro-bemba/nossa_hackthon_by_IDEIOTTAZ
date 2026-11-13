from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ObservationResponse(BaseModel):
    """Resposta de uma observation. `is_mock` é deliberado — ver PDF §4."""

    model_config = ConfigDict(from_attributes=True)

    value_mm: float
    date: date
    lat: float
    lon: float
    source: str
    version: str
    quality_score: float
    ingested_at: datetime
    is_mock: bool


class CombinedResponse(BaseModel):
    observations: list[ObservationResponse]
    errors: dict[str, str] = Field(default_factory=dict)
    divergence: float | None = Field(
        default=None,
        description="Divergência máxima entre pares, em fracção (0.0-1.0). None se <2 fontes.",
    )


class ProvidersListResponse(BaseModel):
    providers: list[str]
    mock_providers: list[str]