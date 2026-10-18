import pytest
from httpx import AsyncClient, ASGITransport
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from backend.app.main import app

@pytest.mark.asyncio
async def test_get_datasets_list():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/datasets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # demo dataset should be in the list
    demo = next((d for d in data if d["id"] == "demo"), None)
    assert demo is not None
    assert demo["kind"] == "synthetic"
    assert "total_pm25_mean" in demo

@pytest.mark.asyncio
async def test_get_dataset_detail():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/datasets/demo")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "demo"
    assert "components" in data["results"]
    assert len(data["results"]["components"]) == 5

@pytest.mark.asyncio
async def test_get_dataset_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/datasets/non_existent_id")
    assert response.status_code == 404
