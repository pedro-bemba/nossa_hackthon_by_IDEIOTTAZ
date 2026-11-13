from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuração da aplicação, lida do ambiente / ficheiro .env."""

    app_env: str = "development"
    app_name: str = "NOSSA Campo"
    database_url: str = "sqlite:///./nossa_campo.db"

    # Sem valor por omissão: a app recusa arrancar sem chave definida.
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    weather_provider: str = "chirps"

    return Settings()