import pytest
from fastapi.testclient import TestClient
from backend.risk.api import app
from backend.risk.bootstrap import bootstrap

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv("DATABASE_URL",f"sqlite:///{tmp_path/'test.db'}")
    monkeypatch.setenv("AGENT_MODE","demo")
    bootstrap()
    with TestClient(app,base_url="http://localhost",headers={"X-Meridian-Action":"analyst"}) as session:
        yield session

