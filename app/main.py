from fastapi import FastAPI

from app.api.routes import health
from app.core.config import get_settings

from app.api.routes import health, weather  # ← adicionar weather

def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        description="Seguro Agrícola Paramétrico. O seguro que cai com a chuva.",
        version="0.1.0",
    )
    app.include_router(health.router)
    app.include_router(weather.router)

    return app


app = create_app()