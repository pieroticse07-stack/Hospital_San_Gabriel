"""Errores de dominio compartidos entre capas."""


class DatabaseError(Exception):
    """Fallo al comunicarse o ejecutar comandos en SQL Server."""


class PacienteNoEncontrado(Exception):
    def __init__(self, paciente_id: int) -> None:
        self.paciente_id = paciente_id
        super().__init__(f"No existe un paciente con ID {paciente_id}")


class PacienteDuplicado(Exception):
    def __init__(self, detalle: str) -> None:
        self.detalle = detalle
        super().__init__(f"Ya existe un paciente con los datos proporcionados: {detalle}")
