"""Modelos Pydantic para la entidad Paciente compartidos entre capas."""

from pydantic import BaseModel, Field


class PacienteBase(BaseModel):
    Nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del paciente")
    Email: str = Field(..., min_length=3, max_length=100, description="Correo electrónico")
    Telefono: str = Field(..., min_length=1, max_length=20, description="Teléfono de contacto")
    Ciudad: str = Field(..., min_length=1, max_length=100, description="Ciudad de residencia")
    Edad: int = Field(..., ge=0, le=150, description="Edad del paciente")


class PacienteCreate(PacienteBase):
    """Payload para crear un paciente (POST)."""
    pass


class PacienteUpdate(BaseModel):
    """Payload para actualizar un paciente (PUT). Campos opcionales."""
    Nombre: str | None = Field(default=None, min_length=1, max_length=100)
    Email: str | None = Field(default=None, min_length=3, max_length=100)
    Telefono: str | None = Field(default=None, min_length=1, max_length=20)
    Ciudad: str | None = Field(default=None, min_length=1, max_length=100)
    Edad: int | None = Field(default=None, ge=0, le=150)


class Paciente(PacienteBase):
    """Modelo completo devuelto por la API, incluye PacienteID autogenerado."""
    PacienteID: int = Field(..., description="ID único y clave primaria del paciente")
