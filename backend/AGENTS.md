# AGENTS.md

`uv`-managed Python 3.14 + FastAPI backend. Persistence is **SQL Server via raw SQL** — there is no ORM and none should be introduced.

## Required architecture

Requests flow in one direction: `main.py -> apis -> services -> repositories`, with `schemas` holding the Pydantic models.

- `apis/` — HTTP routing and request/response handling only; no business logic, no SQL.
- `services/` — business logic; may call repositories, never the other way around.
- `repositories/` — the **only** place that touches SQL Server.
- `schemas/` — Pydantic models shared across layers.
- Don't skip layers (e.g. never call a repository from an API module).

Keep these under `src/backend/` to match the src-layout (e.g. `src/backend/main.py`), which makes the app importable as `backend.main:app`.

## Database rules

- SQL Server, accessed with plain SQL through a driver. **No ORM**: no SQLAlchemy ORM, Django ORM, or equivalent.
- Connection settings live in a `.env` file at the repo root. Never hardcode credentials or commit `.env`.

## Commands

- `uv run uvicorn backend.main:app --reload` — Iniciar el servidor de desarrollo.
