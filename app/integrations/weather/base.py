from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime

@dataclass(frozen=True)
class Observation:
    value_mm: float
    date: date
    lat: float
    lon: float
    source: str
    version: str
    quality_score: float
    ingested_at: datetime

    def __post_init__(self) -> None:
        if not 0.0 <= self.quality_score <= 1.0:
            raise ValueError(f"quality_score deve estar em [0,1], recebido {self.quality_score}")
        if self.value_mm < 0:
            raise ValueError(f"value_mm não pode ser negativo, recebido {self.value_mm}")

class WeatherProvider(ABC):
    name: str

    @abstractmethod
    def get_observation(self, lat: float, lon: float, day: date) -> Observation: ...