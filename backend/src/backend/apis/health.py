"""Endpoint de salud: comprueba la conexión con SQL Server."""

from fastapi import APIRouter, HTTPException, status

from backend.errors import DatabaseError
from backend.repositories import db

router = APIRouter(tags=["health"])


@router.get("/health", summary="Estado del servicio y de la base de datos")
def health() -> dict[str, str]:
    try:
        db.ping()
    except DatabaseError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se puede conectar con la base de datos",
        ) from exc
    return {"status": "ok", "database": "ok"}
