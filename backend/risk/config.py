import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env", override=False)
RUNTIME = ROOT / ".runtime"
AS_OF = "2026-06-30"
DIM = 384


def database_url() -> str:
    return os.getenv("DATABASE_URL") or f"sqlite:///{RUNTIME / 'meridian.db'}"


def mode() -> str:
    value = os.getenv("AGENT_MODE", "demo")
    if value not in {"demo", "live"}:
        raise ValueError("AGENT_MODE must be demo or live")
    return value
