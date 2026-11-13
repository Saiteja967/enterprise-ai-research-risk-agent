"""Deterministic, local feature hashing shared by SQLite and pgvector."""
import hashlib
import math
import re
from sqlalchemy import select
from sqlalchemy.engine import Connection
from .config import DIM
from .models import Evidence
from .schema_v1 import chunks, documents

STOP = set("the and for with that this from company analyze summarise summarize identify actions recommend follow key changes signals risk what are about".split())
def embed(text: str) -> list[float]:
    vector = [0.0] * DIM
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        if token in STOP:
            continue
        digest = hashlib.blake2b(token.encode(), digest_size=4).digest()
        vector[int.from_bytes(digest, "big") % DIM] += 1
    norm = math.sqrt(sum(x*x for x in vector)) or 1
    return [x / norm for x in vector]

def add_document(conn: Connection, doc_id: str, company: str, title: str, kind: str, digest: str, at: str, entries: list[tuple[str,str]]) -> None:
    conn.execute(documents.insert().values(id=doc_id,company=company,title=title,kind=kind,digest=digest,added=at))
    conn.execute(chunks.insert(), [{"id":f"{doc_id}-{i:03}", "document":doc_id, "locator":locator, "body":body, "embedding":embed(title+" "+body)} for i,(locator,body) in enumerate(entries,1)])

def search(conn: Connection, company: str, question: str) -> list[Evidence]:
    vector = embed(question)
    stmt = select(chunks.c.id, documents.c.title, chunks.c.locator, chunks.c.body).join(documents).where(documents.c.company == company)
    if conn.dialect.name == "postgresql":
        distance = chunks.c.embedding.cosine_distance(vector)
        rows = conn.execute(stmt.where(distance < 0.99999).order_by(distance, chunks.c.id).limit(3)).mappings().all()
    else:
        pool = conn.execute(stmt.add_columns(chunks.c.embedding)).mappings()
        ranked = [(sum(a*b for a,b in zip(vector, r["embedding"],strict=True)),r) for r in pool]
        rows = [r for score,r in sorted(ranked,key=lambda x:(-x[0],x[1]["id"])) if score>0.00001][:3]
    return [Evidence(id=r["id"],title=r["title"],locator=r["locator"],body=r["body"],kind="document") for r in rows]

