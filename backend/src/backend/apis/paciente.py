"""Endpoints HTTP de pacientes: solo enrutamiento y traducción a HTTP."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from backend.schemas.paciente import Paciente, PacienteCreate, PacienteUpdate
from backend.services.paciente_service import PacienteService

router = APIRouter(prefix="/pacientes", tags=["pacientes"])

PacienteIdPath = Annotated[int, Path(ge=1, description="ID del paciente")]


def get_paciente_service() -> PacienteService:
    return PacienteService()


ServiceDep = Annotated[PacienteService, Depends(get_paciente_service)]


@router.get("", response_model=list[Paciente], summary="Listar pacientes")
def listar_pacientes(service: ServiceDep) -> list[Paciente]:
    return service.listar()


@router.get("/{paciente_id}", response_model=Paciente, summary="Obtener un paciente")
def obtener_paciente(paciente_id: PacienteIdPath, service: ServiceDep) -> Paciente:
    return service.obtener(paciente_id)


@router.post(
    "",
    response_model=Paciente,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un paciente",
    responses={status.HTTP_409_CONFLICT: {"description": "El paciente ya existe"}},
)
def crear_paciente(datos: PacienteCreate, service: ServiceDep) -> Paciente:
    return service.crear(datos)


@router.put(
    "/{paciente_id}",
    response_model=Paciente,
    summary="Actualizar datos de un paciente",
    responses={status.HTTP_404_NOT_FOUND: {"description": "El paciente no existe"}},
)
def actualizar_paciente(
    paciente_id: PacienteIdPath, datos: PacienteUpdate, service: ServiceDep
) -> Paciente:
    return service.actualizar(paciente_id, datos)


@router.delete(
    "/{paciente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un paciente",
    responses={status.HTTP_404_NOT_FOUND: {"description": "El paciente no existe"}},
)
def eliminar_paciente(paciente_id: PacienteIdPath, service: ServiceDep) -> None:
    service.eliminar(paciente_id)
