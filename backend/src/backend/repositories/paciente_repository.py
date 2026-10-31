"""Acceso a la tabla dbo.Pacientes mediante SQL crudo (sin ORM)."""

import pyodbc

from backend.errors import DatabaseError, PacienteDuplicado
from backend.repositories import db
from backend.schemas.paciente import Paciente, PacienteCreate, PacienteUpdate

_COLUMNS = "PacienteID, Nombre, Email, Telefono, Ciudad, Edad"


def _to_paciente(row: tuple | pyodbc.Row) -> Paciente:
    return Paciente(
        PacienteID=row[0],
        Nombre=row[1],
        Email=row[2],
        Telefono=row[3],
        Ciudad=row[4],
        Edad=row[5],
    )


def _describe(exc: pyodbc.Error) -> str:
    return str(exc).strip() or exc.__class__.__name__


class PacienteRepository:
    def listar(self) -> list[Paciente]:
        try:
            rows = db.fetch_all(f"SELECT {_COLUMNS} FROM dbo.Pacientes ORDER BY PacienteID")
        except pyodbc.Error as exc:
            raise DatabaseError(_describe(exc)) from exc
        return [_to_paciente(row) for row in rows]

    def obtener(self, paciente_id: int) -> Paciente | None:
        try:
            row = db.fetch_one(
                f"SELECT {_COLUMNS} FROM dbo.Pacientes WHERE PacienteID = ?",
                (paciente_id,),
            )
        except pyodbc.Error as exc:
            raise DatabaseError(_describe(exc)) from exc
        return _to_paciente(row) if row is not None else None

    def existe(self, paciente_id: int) -> bool:
        try:
            row = db.fetch_one(
                "SELECT 1 FROM dbo.Pacientes WHERE PacienteID = ?",
                (paciente_id,),
            )
        except pyodbc.Error as exc:
            raise DatabaseError(_describe(exc)) from exc
        return row is not None

    def crear(self, datos: PacienteCreate) -> Paciente:
        sql = (
            "INSERT INTO dbo.Pacientes (Nombre, Email, Telefono, Ciudad, Edad) "
            "OUTPUT INSERTED.PacienteID, INSERTED.Nombre, INSERTED.Email, "
            "       INSERTED.Telefono, INSERTED.Ciudad, INSERTED.Edad "
            "VALUES (?, ?, ?, ?, ?)"
        )
        params = (datos.Nombre, datos.Email, datos.Telefono, datos.Ciudad, datos.Edad)
        try:
            row = db.fetch_one_write(sql, params)
            if row is None:
                raise DatabaseError("No se obtuvo el registro recién insertado.")
            return _to_paciente(row)
        except pyodbc.IntegrityError as exc:
            raise PacienteDuplicado(f"conflicto de integridad con email '{datos.Email}'") from exc
        except pyodbc.Error as exc:
            raise DatabaseError(_describe(exc)) from exc

    def actualizar(self, paciente_id: int, datos: PacienteUpdate) -> bool:
        campos = {k: v for k, v in datos.model_dump().items() if v is not None}
        if not campos:
            return True
        set_clause = ", ".join(f"{col} = ?" for col in campos)
        valores = tuple(campos.values()) + (paciente_id,)
        try:
            affected = db.execute(
                f"UPDATE dbo.Pacientes SET {set_clause} WHERE PacienteID = ?",
                valores,
            )
        except pyodbc.IntegrityError as exc:
            raise PacienteDuplicado("conflicto de integridad al actualizar") from exc
        except pyodbc.Error as exc:
            raise DatabaseError(_describe(exc)) from exc
        return affected > 0

    def eliminar(self, paciente_id: int) -> bool:
        try:
            affected = db.execute(
                "DELETE FROM dbo.Pacientes WHERE PacienteID = ?",
                (paciente_id,),
            )
        except pyodbc.Error as exc:
            raise DatabaseError(_describe(exc)) from exc
        return affected > 0
