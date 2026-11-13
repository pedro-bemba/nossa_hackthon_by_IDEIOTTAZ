from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db

router = APIRouter(tags=["sistema"])


@router.get("/health")
def health() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}


@router.get("/health/db")
def health_db(db: Session = Depends(get_db)) -> dict[str, str]:
    """Prova que o caminho FastAPI → get_db → SQLite funciona."""
    result = db.execute(text("SELECT sqlite_version()")).scalar()
    return {"status": "ok", "database": "connected", "sqlite_version": str(result)}

