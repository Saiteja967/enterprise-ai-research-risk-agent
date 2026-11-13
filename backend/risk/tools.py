"""Two first-party read-only tools. Run as a local stdio MCP server."""

from datetime import timedelta
from typing import Annotated, Literal

from mcp.server.fastmcp import FastMCP
from mcp.shared.memory import create_connected_server_and_client_session
from mcp.types import ToolAnnotations
from pydantic import Field, TypeAdapter

from .analytics import ledger_evidence
from .indexing import search
from .models import CompanyId, Evidence
from .read_session import research_connection

mcp = FastMCP("Meridian research", log_level="WARNING")
readonly = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)


@mcp.tool(annotations=readonly)
def risk_snapshot(company: CompanyId) -> list[Evidence]:
    """Read two period totals and open risk alerts for one synthetic company."""
    with research_connection() as conn:
        return ledger_evidence(conn, company)


@mcp.tool(annotations=readonly)
def retrieve_evidence(
    company: CompanyId, question: Annotated[str, Field(min_length=1, max_length=600)]
) -> list[Evidence]:
    """Find up to three relevant approved passages for one company."""
    with research_connection() as conn:
        return search(conn, company, question)


async def invoke(
    name: Literal["risk_snapshot", "retrieve_evidence"], company: str, question: str = ""
) -> list[Evidence]:
    args = {"company": company}
    if name == "retrieve_evidence":
        args["question"] = question
    async with create_connected_server_and_client_session(
        mcp, read_timeout_seconds=timedelta(seconds=4)
    ) as session:
        result = await session.call_tool(name, args)
        if result.isError or result.structuredContent is None:
            raise RuntimeError("Read-only research tool failed")
        return TypeAdapter(list[Evidence]).validate_python(result.structuredContent["result"])


if __name__ == "__main__":
    mcp.run(transport="stdio")
