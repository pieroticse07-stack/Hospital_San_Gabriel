"""Punto de entrada de la API: CORS, routers y traducción de errores a HTTP."""

import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.apis import health, paciente
from backend.config import get_settings
from backend.errors import DatabaseError, PacienteDuplicado, PacienteNoEncontrado

logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="Hospital San Gabriel API",
    description="CRUD de pacientes sobre SQL Server sin ORM.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(paciente.router)
app.include_router(health.router)


@app.exception_handler(PacienteNoEncontrado)
async def _paciente_no_encontrado(
    request: Request, exc: PacienteNoEncontrado
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
    )


@app.exception_handler(PacienteDuplicado)
async def _paciente_duplicado(
    request: Request, exc: PacienteDuplicado
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
    )


@app.exception_handler(DatabaseError)
async def _database_error(request: Request, exc: DatabaseError) -> JSONResponse:
    logger.exception("Error de base de datos en %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": f"Error en base de datos: {str(exc)}"},
    )
