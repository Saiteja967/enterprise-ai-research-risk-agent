"""Cap the entire incoming body before Starlette's multipart parser allocates it."""

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class BodyLimit:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http" or scope["method"] not in {"POST", "PUT", "PATCH"}:
            return await self.app(scope, receive, send)
        limit = 2 * 1024 * 1024 + 8192 if scope["path"] == "/api/documents" else 8192
        raw = bytearray()
        while True:
            msg = await receive()
            if msg["type"] == "http.disconnect":
                return
            if len(raw) + len(msg.get("body", b"")) > limit:
                await JSONResponse({"detail": "Request body exceeds the size limit."}, 413)(
                    scope, receive, send
                )
                return
            raw.extend(msg.get("body", b""))
            if not msg.get("more_body"):
                break
        sent = False

        async def replay() -> Message:
            nonlocal sent
            if sent:
                return await receive()
            sent = True
            return {"type": "http.request", "body": bytes(raw), "more_body": False}

        return await self.app(scope, replay, send)
