"""Configuración de la aplicación cargada desde el archivo .env."""

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    db_server: str
    db_name: str
    db_user: str
    db_password: str
    db_driver: str
    cors_origins: tuple[str, ...]

    @property
    def connection_string(self) -> str:
        """Cadena de conexión para pyodbc (sin ORM)."""
        return (
            f"DRIVER={{{self.db_driver}}};"
            f"SERVER={self.db_server};"
            f"DATABASE={self.db_name};"
            f"UID={self.db_user};"
            f"PWD={self.db_password};"
            "TrustServerCertificate=yes;"
        )


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(
            f"Falta la variable de entorno '{name}'. "
            f"Configúrala en {REPO_ROOT / '.env'}."
        )
    return value


def _parse_origins(raw: str) -> tuple[str, ...]:
    origins = tuple(origin.strip() for origin in raw.split(",") if origin.strip())
    if not origins:
        return ("http://localhost:4200", "http://127.0.0.1:4200")
    return origins


@lru_cache
def get_settings() -> Settings:
    return Settings(
        db_server=_required("DB_SERVER"),
        db_name=_required("DB_NAME"),
        db_user=_required("DB_USER"),
        db_password=_required("DB_PASSWORD"),
        db_driver=os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server").strip(),
        cors_origins=_parse_origins(os.getenv("CORS_ORIGINS", "http://localhost:4200,http://127.0.0.1:4200")),
    )
