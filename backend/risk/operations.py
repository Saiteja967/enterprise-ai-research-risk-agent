from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request, UploadFile
from sqlalchemy import case, func, select
from sqlalchemy.exc import IntegrityError
from starlette.concurrency import run_in_threadpool

from .control import AlertChange, Confirm, Decision, Proposal, decide, proposal, stage
from .db import database, record
from .evaluation import Evaluation, evaluate
from .ingest import MAX_BYTES, stage_file
from .models import CompanyId, Model, Report
from .schema_v1 import alerts, approvals, audit, chunks, companies, documents, evaluations, runs

router = APIRouter(prefix="/api")


class DocumentRow(Model):
    id: str
    company: str
    title: str
    kind: str
    added: str
    chunks: int


class Event(Model):
    id: str
    at: str
    event: str
    subject: str
    request_id: str


@router.get("/reports", response_model=list[Report])
def history():
    with database().connect() as conn:
        return list(
            conn.scalars(
                select(runs.c.report).order_by(runs.c.at.desc(), runs.c.id.desc()).limit(100)
            )
        )


@router.get("/documents", response_model=list[DocumentRow])
def library():
    with database().connect() as conn:
        count = select(func.count()).where(chunks.c.document == documents.c.id).scalar_subquery()
        stmt = select(
            documents.c.id,
            documents.c.company,
            documents.c.title,
            documents.c.kind,
            documents.c.added,
            count.label("chunks"),
        ).order_by(documents.c.added.desc(), documents.c.id)
        return list(conn.execute(stmt).mappings())


@router.post("/documents", response_model=Proposal, status_code=201)
async def upload(
    request: Request,
    file: UploadFile,
    company: Annotated[CompanyId, Form()],
    confirm: Annotated[str, Form()],
):
    if confirm != "true":
        raise HTTPException(422, "Confirm the submission for review.")
    with database().connect() as conn:
        if not conn.scalar(select(companies.c.id).where(companies.c.id == company)):
            raise HTTPException(404, "Unknown company.")
    try:
        raw = await file.read(MAX_BYTES + 1)
        payload = await run_in_threadpool(stage_file, file.filename or "", raw)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    finally:
        await file.close()
    with database().begin() as conn:
        return stage(
            conn, company, "document.ingest", payload["title"], payload, request.state.request_id
        )


@router.post("/alert-reviews", response_model=Proposal, status_code=201)
def review(body: AlertChange, request: Request):
    with database().begin() as conn:
        item = conn.execute(select(alerts).where(alerts.c.id == body.alert)).mappings().first()
        if not item:
            raise HTTPException(404, "Unknown alert.")
        if item["status"] != "open":
            raise HTTPException(409, "Alert already reviewed.")
        return stage(
            conn,
            item["company"],
            "alert.review",
            item["title"],
            {"alert": body.alert},
            request.state.request_id,
        )


@router.get("/approvals", response_model=list[Proposal])
def queue():
    with database().connect() as conn:
        return [
            proposal(r)
            for r in conn.execute(
                select(approvals)
                .order_by(
                    case((approvals.c.status == "pending", 0), else_=1),
                    approvals.c.at.desc(),
                    approvals.c.id.desc(),
                )
                .limit(200)
            ).mappings()
        ]


@router.post("/approvals/{pk}", response_model=Proposal)
def resolve(pk: str, body: Decision, request: Request):
    try:
        with database().begin() as conn:
            return decide(conn, pk, body.decision, request.state.request_id)
    except IntegrityError as exc:
        raise HTTPException(409, "Concurrent document update. Retry this decision.") from exc


@router.get("/audit", response_model=list[Event])
def events():
    with database().connect() as conn:
        return list(
            conn.execute(
                select(audit).order_by(audit.c.at.desc(), audit.c.id.desc()).limit(200)
            ).mappings()
        )


@router.get("/evaluations", response_model=Evaluation | None)
def last_evaluation():
    with database().connect() as conn:
        return conn.scalar(select(evaluations.c.result).order_by(evaluations.c.at.desc()).limit(1))


@router.post("/evaluations", response_model=Evaluation, status_code=201)
async def score(body: Confirm, request: Request):
    result = await evaluate()
    with database().begin() as conn:
        conn.execute(
            evaluations.insert().values(id=result.id, at=result.at, result=result.model_dump())
        )
        record(conn, "evaluation.completed", result.id, request.state.request_id)
    return result
