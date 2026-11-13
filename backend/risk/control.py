from typing import Literal

from fastapi import HTTPException
from pydantic import Field
from sqlalchemy import select, update
from sqlalchemy.engine import Connection

from .db import now, record, uid
from .indexing import add_document
from .models import CompanyId, Model
from .schema_v1 import alerts, approvals, documents


class Confirm(Model):
    confirm: Literal[True]


class Decision(Confirm):
    decision: Literal["approve", "reject"]


class AlertChange(Confirm):
    alert: str = Field(min_length=1, max_length=32)


class Proposal(Model):
    id: str
    company: CompanyId
    at: str
    title: str
    kind: str
    status: str
    preview: str


def proposal(row) -> Proposal:
    payload = row["payload"]
    preview = (
        " · ".join([f"{len(payload['entries'])} chunks", payload["entries"][0][1][:280]])
        if row["kind"] == "document.ingest"
        else f"{payload['alert']} · open → reviewed"
    )
    return Proposal(
        **{k: row[k] for k in ["id", "company", "at", "title", "kind", "status"]}, preview=preview
    )


def stage(
    conn: Connection, company: str, kind: str, title: str, payload: dict, request_id: str
) -> Proposal:
    pk = uid("APR")
    values = dict(
        id=pk,
        company=company,
        at=now(),
        kind=kind,
        title=title,
        status="pending",
        payload=payload,
    )
    conn.execute(approvals.insert().values(**values))
    record(conn, "approval.requested", pk, request_id)
    return proposal(values)


def decide(conn: Connection, pk: str, decision: str, request_id: str) -> Proposal:
    status = "approved" if decision == "approve" else "rejected"
    item = (
        conn.execute(
            update(approvals)
            .where(approvals.c.id == pk, approvals.c.status == "pending")
            .values(status=status)
            .returning(*approvals.c)
        )
        .mappings()
        .first()
    )
    if item is None:
        existing = conn.execute(select(approvals).where(approvals.c.id == pk)).mappings().first()
        if existing is None:
            raise HTTPException(404, "Unknown approval.")
        if existing["status"] != status:
            raise HTTPException(409, "This request already has a different decision.")
        return proposal(existing)
    payload = item["payload"]
    if status == "approved":
        if item["kind"] == "document.ingest":
            duplicate = conn.scalar(
                select(documents.c.id).where(
                    documents.c.company == item["company"], documents.c.digest == payload["digest"]
                )
            )
            if not duplicate:
                add_document(
                    conn,
                    uid("DOC"),
                    item["company"],
                    payload["title"],
                    payload["kind"],
                    payload["digest"],
                    now(),
                    payload["entries"],
                )
        else:
            conn.execute(
                update(alerts)
                .where(
                    alerts.c.id == payload["alert"],
                    alerts.c.company == item["company"],
                    alerts.c.status == "open",
                )
                .values(status="reviewed")
            )
    record(conn, f"approval.{status}", pk, request_id)
    return proposal(item)
