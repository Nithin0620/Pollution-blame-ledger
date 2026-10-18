import pytest
from httpx import AsyncClient, ASGITransport
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from backend.app.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "service": "pollution-blame-ledger-api"}

@pytest.mark.asyncio
async def test_openapi_schema_generated():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/openapi.json")
    assert res.status_code == 200
    schema = res.json()
    assert "paths" in schema
    assert "/api/datasets" in schema["paths"]
    assert "/api/simulate/interventions" in schema["paths"]
    assert "/api/upload/validate" in schema["paths"]
    assert "/api/jobs/run" in schema["paths"]
