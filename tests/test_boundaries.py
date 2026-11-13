import asyncio
from unittest.mock import patch

import httpx
import pytest
from langchain_openai import ChatOpenAI
from sqlalchemy.exc import DBAPIError

from backend.risk import provider
from backend.risk.models import Evidence
from backend.risk.read_session import research_connection


def test_read_scope_denies_writes(client):
    with research_connection() as conn, pytest.raises(DBAPIError):
        conn.exec_driver_sql("UPDATE alerts SET status='reviewed' WHERE 1=0")
    r = client.post("/api/alert-reviews", json={"confirm": True, "alert": "AL-1048"})
    assert r.status_code == 201


def test_model_adapter_structured_contract_and_usage(monkeypatch):
    for name, value in [
        ("INPUT_USD_PER_M", "2"),
        ("CACHED_INPUT_USD_PER_M", "1"),
        ("OUTPUT_USD_PER_M", "8"),
    ]:
        monkeypatch.setenv(name, value)
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4.1-mini")

    async def exercise():
        def reply(request):
            import json

            payload = json.loads(request.content)
            assert payload["response_format"]["type"] == "json_schema"
            assert "tools" not in payload
            return httpx.Response(
                200,
                json={
                    "id": "chatcmpl-fixture",
                    "object": "chat.completion",
                    "created": 1,
                    "model": "gpt-4.1-mini",
                    "choices": [
                        {
                            "index": 0,
                            "finish_reason": "stop",
                            "message": {
                                "role": "assistant",
                                "content": '{"citations":["AL-1048"],"actions":["collections"]}',
                            },
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 10,
                        "total_tokens": 110,
                        "prompt_tokens_details": {"cached_tokens": 20},
                    },
                },
            )

        async with httpx.AsyncClient(transport=httpx.MockTransport(reply)) as client:

            def mocked(**kwargs):
                return ChatOpenAI(
                    **kwargs,
                    api_key="test-fixture",
                    base_url="http://fixture.invalid/v1",
                    http_async_client=client,
                )

            with patch.object(provider, "ChatOpenAI", mocked):
                source = Evidence(
                    id="AL-1048",
                    kind="alert",
                    locator="June",
                    title="Receivables",
                    body="Two accounts overdue.",
                )
                return await provider.live_select("Investigate collections.", [source])

    selection, usage = asyncio.run(exercise())
    assert selection.citations == ["AL-1048"]
    assert usage.input_tokens == 100 and usage.cached_tokens == 20 and usage.output_tokens == 10
    assert usage.cost_usd == pytest.approx(0.00026)
