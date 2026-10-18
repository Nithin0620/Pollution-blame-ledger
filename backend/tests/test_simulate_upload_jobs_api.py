import pytest
import io
from httpx import AsyncClient, ASGITransport
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from backend.app.main import app

@pytest.mark.asyncio
async def test_simulate_interventions():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {
            "dataset_id": "demo",
            "cuts": {
                "traffic": 50,
                "biomass": 0,
                "dust": 50,
                "industry": 0
            }
        }
        res = await ac.post("/api/simulate/interventions", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "new_pm25" in data
    assert data["new_pm25"] < data["original_pm25"]
    assert "averted_deaths_mean" in data
    assert data["averted_deaths_mean"] > 0

@pytest.mark.asyncio
async def test_upload_validate_valid_csv():
    # Construct a valid small CSV with required headers
    csv_content = """year,month,day,hour,PM2.5,PM10,NO2,SO2,CO,WS,WD,SR,AT
2025,11,1,0,120.5,240.0,45.2,12.0,1.5,1.2,280,0,18.0
2025,11,1,1,130.0,260.0,48.0,13.0,1.7,1.0,290,0,17.5
"""
    files = {"file": ("test.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/upload/validate", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert data["row_count"] == 2
    assert "PM2.5" in data["columns_present"]
    assert len(data["columns_missing"]) == 0

@pytest.mark.asyncio
async def test_upload_validate_missing_columns():
    csv_content = """year,month,day,hour,PM2.5
2025,11,1,0,120.5
"""
    files = {"file": ("bad.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/upload/validate", files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is False
    assert len(data["columns_missing"]) > 0

@pytest.mark.asyncio
async def test_job_runner_lifecycle():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        start_res = await ac.post("/api/jobs/run", json={"type": "demo", "config": {}})
        assert start_res.status_code == 200
        job_data = start_res.json()
        job_id = job_data["job_id"]
        assert job_data["status"] in ["queued", "running", "completed"]

        poll_res = await ac.get(f"/api/jobs/{job_id}")
        assert poll_res.status_code == 200
        status_data = poll_res.json()
        assert status_data["job_id"] == job_id
