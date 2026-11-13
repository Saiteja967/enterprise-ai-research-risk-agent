from sqlalchemy import func, select
from sqlalchemy.engine import Connection
from .models import Alert, Company, Evidence, Overview, Period
from .config import AS_OF, mode
from .schema_v1 import alerts, approvals, companies, documents, runs, transactions

def series(conn: Connection, company: str | None = None) -> list[Period]:
    stmt = select(transactions.c.period,func.sum(transactions.c.amount).label("amount"),func.sum(transactions.c.overdue).label("overdue")).group_by(transactions.c.period).order_by(transactions.c.period)
    if company:
        stmt = stmt.where(transactions.c.company==company)
    return [Period.model_validate(r) for r in conn.execute(stmt).mappings()]

def overview(conn: Connection) -> Overview:
    return Overview(as_of=AS_OF, mode=mode(),companies=[Company.model_validate(r) for r in conn.execute(select(companies).order_by(companies.c.id)).mappings()],alerts=[Alert.model_validate(r) for r in conn.execute(select(alerts).order_by(alerts.c.opened.desc())).mappings()],periods=series(conn),reports=conn.scalar(select(func.count()).select_from(runs)) or 0,documents=conn.scalar(select(func.count()).select_from(documents)) or 0,pending=conn.scalar(select(func.count()).select_from(approvals).where(approvals.c.status=="pending")) or 0)

def ledger_evidence(conn: Connection,company: str) -> list[Evidence]:
    history = series(conn,company)
    out=[]
    if len(history)>=2:
        prev, latest=history[-2:]
        out.append(Evidence(id=f"SQL-{company}-{latest.period}",title="Monthly receivables ledger",locator=f"{company} · {prev.period} / {latest.period}",kind="ledger",body=f"Overdue receivables changed from ${prev.overdue:,} in {prev.period} to ${latest.overdue:,} in {latest.period}. Total receivables in {latest.period} were ${latest.amount:,}."))
    for row in conn.execute(select(alerts).where(alerts.c.company==company,alerts.c.status=="open").order_by(alerts.c.opened.desc()).limit(8)).mappings():
        out.append(Evidence(id=row["id"],title=row["title"],locator=f"Alert register · {row['opened']}",kind="alert",body=f"{row['severity'].title()} severity. {row['detail']}"))
    return out

