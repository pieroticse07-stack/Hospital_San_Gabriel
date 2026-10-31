"""Único punto de acceso a SQL Server: conexión y cursores con pyodbc (sin ORM)."""

from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from typing import Any

import pyodbc

from backend.config import get_settings
from backend.errors import DatabaseError


def connect() -> pyodbc.Connection:
    """Abre una conexión nueva usando las credenciales del .env."""
    return pyodbc.connect(get_settings().connection_string, timeout=10)


@contextmanager
def _cursor(commit: bool) -> Iterator[pyodbc.Cursor]:
    connection = connect()
    try:
        cursor = connection.cursor()
        try:
            yield cursor
            if commit:
                connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
    finally:
        connection.close()


def read_cursor() -> Iterator[pyodbc.Cursor]:
    return _cursor(commit=False)


def write_cursor() -> Iterator[pyodbc.Cursor]:
    return _cursor(commit=True)


def fetch_all(sql: str, params: Sequence[Any] = ()) -> list[tuple]:
    with read_cursor() as cursor:
        cursor.execute(sql, params)
        return [tuple(row) for row in cursor.fetchall()]


def fetch_one(sql: str, params: Sequence[Any] = ()) -> tuple | None:
    with read_cursor() as cursor:
        cursor.execute(sql, params)
        row = cursor.fetchone()
        return tuple(row) if row is not None else None


def fetch_one_write(sql: str, params: Sequence[Any] = ()) -> tuple | None:
    """Ejecuta una sentencia de inserción/escritura con OUTPUT y confirma la transacción."""
    with write_cursor() as cursor:
        cursor.execute(sql, params)
        row = cursor.fetchone()
        return tuple(row) if row is not None else None


def execute(sql: str, params: Sequence[Any] = ()) -> int:
    """Ejecuta una sentencia de escritura (UPDATE/DELETE) y devuelve filas afectadas."""
    with write_cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.rowcount


def ping() -> None:
    try:
        fetch_one("SELECT 1")
    except pyodbc.Error as exc:
        raise DatabaseError(str(exc).strip() or exc.__class__.__name__) from exc
