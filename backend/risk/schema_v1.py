"""Immutable schema for migration 0001 and Core query definitions."""
from sqlalchemy import JSON, Column, ForeignKey, Integer, MetaData, String, Table, Text, UniqueConstraint
from pgvector.sqlalchemy import Vector
from .config import DIM

meta = MetaData()
def key():
    return Column("id", String(96), primary_key=True)
def company_key():
    return Column("company", ForeignKey("companies.id"), nullable=False, index=True)

companies = Table("companies", meta, key(), Column("name", String, nullable=False), Column("sector", String, nullable=False))
transactions = Table("transactions", meta, key(), company_key(), Column("period", String(7), nullable=False), Column("amount", Integer, nullable=False), Column("overdue", Integer, nullable=False))
alerts = Table("alerts", meta, key(), company_key(), Column("title", String, nullable=False), Column("severity", String, nullable=False), Column("detail", Text, nullable=False), Column("status", String, nullable=False), Column("opened", String, nullable=False))
documents = Table("documents", meta, key(), company_key(), Column("title", String, nullable=False), Column("kind", String, nullable=False), Column("digest", String, nullable=False), Column("added", String, nullable=False), UniqueConstraint("company","digest"))
chunks = Table("chunks", meta, key(), Column("document", ForeignKey("documents.id"), nullable=False, index=True), Column("locator", String, nullable=False), Column("body", Text, nullable=False), Column("embedding", Vector(DIM).with_variant(JSON(), "sqlite"), nullable=False))
runs = Table("runs", meta, key(), company_key(), Column("at", String, nullable=False), Column("report", JSON, nullable=False))
approvals = Table("approvals", meta, key(), company_key(), Column("at", String, nullable=False), Column("kind", String, nullable=False), Column("title", String, nullable=False), Column("status", String, nullable=False), Column("payload", JSON, nullable=False))
audit = Table("audit", meta, key(), Column("at", String, nullable=False), Column("event", String, nullable=False), Column("subject", String, nullable=False), Column("request_id", String, nullable=False))
evaluations = Table("evaluations", meta, key(), Column("at", String, nullable=False), Column("result", JSON, nullable=False))

