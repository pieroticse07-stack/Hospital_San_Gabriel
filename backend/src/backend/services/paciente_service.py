"""Reglas de negocio de pacientes."""

from backend.errors import PacienteNoEncontrado
from backend.repositories.paciente_repository import PacienteRepository
from backend.schemas.paciente import Paciente, PacienteCreate, PacienteUpdate


class PacienteService:
    def __init__(self, repository: PacienteRepository | None = None) -> None:
        self._repository = repository or PacienteRepository()

    def listar(self) -> list[Paciente]:
        return self._repository.listar()

    def obtener(self, paciente_id: int) -> Paciente:
        paciente = self._repository.obtener(paciente_id)
        if paciente is None:
            raise PacienteNoEncontrado(paciente_id)
        return paciente

    def crear(self, datos: PacienteCreate) -> Paciente:
        return self._repository.crear(datos)

    def actualizar(self, paciente_id: int, datos: PacienteUpdate) -> Paciente:
        if not self._repository.existe(paciente_id):
            raise PacienteNoEncontrado(paciente_id)
        self._repository.actualizar(paciente_id, datos)
        paciente = self._repository.obtener(paciente_id)
        if paciente is None:
            raise PacienteNoEncontrado(paciente_id)
        return paciente

    def eliminar(self, paciente_id: int) -> None:
        if not self._repository.eliminar(paciente_id):
            raise PacienteNoEncontrado(paciente_id)
