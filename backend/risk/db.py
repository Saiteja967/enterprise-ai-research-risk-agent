from contextvars import ContextVar
from datetime import UTC, datetime
from functools import lru_cache
from uuid import uuid4

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Connection, Engine

from .config import database_url
from .schema_v1 import audit


@lru_cache(maxsize=4)
def engine_for(url: str) -> Engine:
    engine = create_engine(url, pool_pre_ping=True)
    if engine.dialect.name == "sqlite":

        @event.listens_for(engine, "connect")
        def pragmas(conn, _record):
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA busy_timeout=10000")

    return engine


db_override: ContextVar[Engine | None] = ContextVar("db_override", default=None)


def database() -> Engine:
    return db_override.get() or engine_for(database_url())


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds")


def uid(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:16]}"


def record(conn: Connection, event_name: str, subject: str, request_id: str) -> None:
    conn.execute(
        audit.insert().values(
            id=uid("EV"), at=now(), event=event_name, subject=subject, request_id=request_id
        )
    )
