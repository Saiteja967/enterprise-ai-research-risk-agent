import json
import logging
from pathlib import Path
from time import perf_counter
from urllib.parse import urlsplit
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .analytics import overview
from .config import ROOT
from .db import database, record
from .limits import BodyLimit
from .models import Overview, Report, ResearchRequest
from .operations import router
from .safety import contains_directive
from .schema_v1 import companies, runs
from .workflow import investigate

app = FastAPI(title="Meridian · Enterprise AI Research & Risk Intelligence Agent", version="1.0.0")
log = logging.getLogger("uvicorn.error")


@app.middleware("http")
async def boundary(request: Request, call_next):
    request.state.request_id = uuid4().hex
    start = perf_counter()
    origin = request.headers.get("origin")
    try:
        foreign = origin and (
            urlsplit(origin).netloc != request.headers.get("host")
            or urlsplit(origin).scheme != request.url.scheme
        )
    except ValueError:
        foreign = True
    if request.method not in {"GET", "HEAD", "OPTIONS"} and (
        foreign or request.headers.get("x-meridian-action") != "analyst"
    ):
        response = JSONResponse({"detail": "Same-origin analyst action required."}, status_code=403)
    else:
        response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; frame-ancestors 'none'; base-uri 'none'"
    )
    log.info(
        json.dumps(
            {
                "request_id": request.state.request_id,
                "method": request.method,
                "route": request.url.path,
                "status": response.status_code,
                "latency_ms": round((perf_counter() - start) * 1000, 2),
            }
        )
    )
    return response


app.include_router(router)
app.add_middleware(BodyLimit)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "[::1]"])


@app.get("/api/health")
def health() -> dict[str, str]:
    with database().connect() as conn:
        conn.execute(select(companies.c.id).limit(1))
    return {"status": "ok"}


@app.get("/api/overview", response_model=Overview)
def get_overview():
    with database().connect() as conn:
        return overview(conn)


def require_company(conn, company: str) -> None:
    if conn.scalar(select(companies.c.id).where(companies.c.id == company)) is None:
        raise HTTPException(404, "Unknown company.")


@app.post("/api/reports", response_model=Report, status_code=201)
async def create_report(body: ResearchRequest, request: Request):
    with database().connect() as conn:
        require_company(conn, body.company)
    if contains_directive(body.question):
        raise HTTPException(422, "Ask a research question without instruction overrides.")
    report = await investigate(body)
    with database().begin() as conn:
        conn.execute(
            runs.insert().values(
                id=report.id, company=report.company, at=report.at, report=report.model_dump()
            )
        )
        record(conn, "report.created", report.id, request.state.request_id)
    log.info(
        json.dumps(
            {
                "event": "research.completed",
                "request_id": request.state.request_id,
                "report_id": report.id,
                "mode": report.mode,
                "model": report.model,
                "status": report.status,
                "latency_ms": report.latency_ms,
                **report.usage.model_dump(),
            }
        )
    )
    return report


def mount_frontend(path: Path = ROOT / "frontend/dist") -> None:
    if path.is_dir():
        app.mount("/", StaticFiles(directory=path, html=True), name="console")
