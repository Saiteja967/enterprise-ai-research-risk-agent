"""Use a dedicated empty PostgreSQL database supplied by the test runner."""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from backend.risk.api import app
from backend.risk.bootstrap import bootstrap
from backend.risk.db import database


@pytest.mark.skipif(
    not os.getenv("TEST_POSTGRES_URL"),
    reason="requires a disposable PostgreSQL + pgvector database",
)
def test_postgres_vector_workflow(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", os.environ["TEST_POSTGRES_URL"])
    monkeypatch.setenv("AGENT_MODE", "demo")
    bootstrap()
    with database().connect() as conn:
        assert conn.scalar(text("SELECT extversion FROM pg_extension WHERE extname = 'vector'"))
        assert conn.scalar(text("SELECT vector_dims(embedding) FROM chunks LIMIT 1")) == 384
    with TestClient(
        app, base_url="http://localhost", headers={"X-Meridian-Action": "analyst"}
    ) as client:
        result = client.post(
            "/api/reports",
            json={
                "company": "KST",
                "question": "Investigate carrier concentration and backup capacity.",
                "confirm": True,
            },
        )
        assert result.status_code == 201, result.text
        report = result.json()
        assert report["status"] == "complete", report["steps"]
        assert "DOC-KST-001" in {r["citation"] for r in report["findings"]}
        pending = client.post(
            "/api/documents",
            data={"confirm": "true", "company": "KST"},
            files={
                "file": (
                    "carrier.csv",
                    b"topic,note\nBackup,Alternate synthetic carrier identified\n",
                )
            },
        ).json()
        assert (
            client.post(
                "/api/approvals/" + pending["id"], json={"decision": "approve", "confirm": True}
            ).status_code
            == 200
        )
    database().dispose()
