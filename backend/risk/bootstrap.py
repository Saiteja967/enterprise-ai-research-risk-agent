import csv
import hashlib
import json

from alembic import command
from alembic.config import Config
from sqlalchemy import select
from sqlalchemy.engine import Connection

from .config import ROOT, RUNTIME
from .db import database
from .indexing import add_document
from .schema_v1 import alerts, companies, documents, transactions


def bootstrap() -> None:
    RUNTIME.mkdir(exist_ok=True)
    command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
    with database().begin() as conn:
        seed_records(conn)


def seed_records(conn: Connection) -> None:
    seed = json.loads((ROOT / "data/portfolio.json").read_text())
    for table, records in [
        (companies, seed["companies"]),
        (transactions, seed["transactions"]),
        (alerts, seed["alerts"]),
    ]:
        present = set(conn.scalars(select(table.c.id)))
        missing = [r for r in records if r["id"] not in present]
        if missing:
            conn.execute(table.insert(), missing)
    with (ROOT / "data/briefings.csv").open(newline="") as handle:
        for row in csv.DictReader(handle):
            if conn.scalar(select(documents.c.id).where(documents.c.id == row["id"])):
                continue
            body = row["body"]
            add_document(
                conn,
                row["id"],
                row["company"],
                row["title"],
                "Seed brief",
                hashlib.sha256(body.encode()).hexdigest(),
                "2026-06-30",
                [("Brief · paragraph 1", body)],
            )


if __name__ == "__main__":
    bootstrap()
