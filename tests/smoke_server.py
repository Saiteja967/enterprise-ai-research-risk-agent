"""Isolate each browser suite from the user's workspace and provider credentials."""

import os
import tempfile

import uvicorn

from backend.risk.bootstrap import bootstrap

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as directory:
        os.environ["DATABASE_URL"] = f"sqlite:///{directory}/smoke.db"
        os.environ["AGENT_MODE"] = "demo"
        bootstrap()
        uvicorn.run("backend.risk.main:app", host="127.0.0.1", port=8174, log_level="warning")
