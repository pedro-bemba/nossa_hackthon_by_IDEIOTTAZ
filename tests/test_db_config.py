"""Prova que o encanamento da BD abre e que os PRAGMAs SQLite estão activos."""

from sqlalchemy import text

from app.db.session import SessionLocal, engine


def test_engine_abre_conexao() -> None:
    with engine.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1


def test_sessionlocal_executa_query() -> None:
    with SessionLocal() as db:
        assert db.execute(text("SELECT 1")).scalar() == 1


def test_foreign_keys_ligadas() -> None:
    with SessionLocal() as db:
        assert db.execute(text("PRAGMA foreign_keys")).scalar() == 1