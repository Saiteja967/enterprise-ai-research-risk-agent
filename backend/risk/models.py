from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from typing_extensions import Annotated

Severity = Literal["high", "medium", "low"]
CompanyId = Annotated[str, StringConstraints(pattern=r"^[A-Z]{2,5}$")]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Company(Model):
    id: str
    name: str
    sector: str


class Alert(Model):
    id: str
    company: str
    title: str
    severity: Severity
    detail: str
    status: str
    opened: str


class Period(Model):
    period: str
    amount: int
    overdue: int


class Evidence(Model):
    id: str
    title: str
    locator: str
    body: str
    kind: Literal["ledger", "alert", "document"]


class Finding(Model):
    citation: str
    text: str


class RiskFactor(Model):
    title: str
    severity: Severity
    citation: str


class Trace(Model):
    node: str
    status: Literal["ok", "warning", "error"]
    detail: str
    ms: float
    tool: str | None = None


class Usage(Model):
    input_tokens: int | None = 0
    cached_tokens: int | None = 0
    output_tokens: int | None = 0
    cost_usd: float | None = 0


class ResearchRequest(Model):
    company: CompanyId
    question: str = Field(min_length=8, max_length=600)
    confirm: Literal[True]


class Report(Model):
    id: str
    at: str
    company: str
    question: str
    mode: str
    model: str
    status: Literal["complete", "partial", "failed"]
    findings: list[Finding]
    summary: str = ""
    risk_factors: list[RiskFactor] = Field(default_factory=list)
    sources: list[Evidence]
    recommendations: list[str]
    confidence: str
    uncertainties: list[str]
    steps: list[Trace]
    usage: Usage
    latency_ms: float


class Overview(Model):
    as_of: str
    companies: list[Company]
    alerts: list[Alert]
    periods: list[Period]
    reports: int
    pending: int
    documents: int
    mode: str
