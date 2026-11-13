from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.engine import Connection

from .db import database


@contextmanager
def research_connection() -> Iterator[Connection]:
    """Enforce the tool permission while the connection is checked out."""
    with database().connect() as conn:
        if conn.dialect.name == "postgresql":
            with conn.begin():
                conn.exec_driver_sql("SET TRANSACTION READ ONLY")
                conn.exec_driver_sql("SET LOCAL statement_timeout = '3500ms'")
                yield conn
        else:
            conn.exec_driver_sql("PRAGMA query_only = ON")
            try:
                yield conn
            finally:
                conn.rollback()
                conn.exec_driver_sql("PRAGMA query_only = OFF")
