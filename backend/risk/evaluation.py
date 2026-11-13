import asyncio
import json
import math
import statistics
import tempfile

from sqlalchemy import create_engine

from .bootstrap import seed_records
from .config import ROOT
from .db import db_override, now, uid
from .models import Model, ResearchRequest
from .schema_v1 import meta
from .workflow import investigate


class Case(Model):
    company: str
    question: str
    recall: float
    exact_support: float
    retrieval_ok: bool
    matched: int
    expected: int
    latency_ms: float


class Evaluation(Model):
    id: str
    at: str
    cases: list[Case]
    mean_recall: float
    mean_support: float
    retrieval_accuracy: float
    p50_ms: float
    p95_ms: float
    tokens: int
    cost_usd: float


async def evaluate() -> Evaluation:
    cases = []
    tokens = 0
    cost = 0.0
    with tempfile.TemporaryDirectory() as tmp:
        engine = create_engine(f"sqlite:///{tmp}/fixture.db")
        try:
            with engine.begin() as conn:
                meta.create_all(conn)
                seed_records(conn)
            token = db_override.set(engine)
            try:
                for row in json.loads((ROOT / "data/evaluation.json").read_text()):
                    report = await investigate(
                        ResearchRequest(
                            company=row["company"], question=row["question"], confirm=True
                        ),
                        simulation=True,
                    )
                    cited = {f.citation for f in report.findings}
                    expected = set(row["expected"])
                    docs = {s.id for s in report.sources if s.kind == "document"}
                    bodies = {s.id: s.body for s in report.sources}
                    support = sum(bodies.get(f.citation) == f.text for f in report.findings) / max(
                        1, len(report.findings)
                    )
                    hit = len(cited & expected)
                    cases.append(
                        Case(
                            company=row["company"],
                            question=row["question"],
                            recall=hit / len(expected),
                            exact_support=support,
                            retrieval_ok=row["document"] in docs if row["document"] else not docs,
                            matched=hit,
                            expected=len(expected),
                            latency_ms=report.latency_ms,
                        )
                    )
                    tokens += (report.usage.input_tokens or 0) + (report.usage.output_tokens or 0)
                    cost += report.usage.cost_usd or 0
            finally:
                db_override.reset(token)
        finally:
            engine.dispose()
    latencies = sorted(c.latency_ms for c in cases)
    return Evaluation(
        id=uid("EVAL"),
        at=now(),
        cases=cases,
        mean_recall=statistics.mean(c.recall for c in cases),
        mean_support=statistics.mean(c.exact_support for c in cases),
        retrieval_accuracy=statistics.mean(c.retrieval_ok for c in cases),
        p50_ms=statistics.median(latencies),
        p95_ms=latencies[math.ceil(len(cases) * 0.95) - 1],
        tokens=tokens,
        cost_usd=cost,
    )


if __name__ == "__main__":
    print(asyncio.run(evaluate()).model_dump_json(indent=2))
