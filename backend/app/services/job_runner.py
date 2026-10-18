import asyncio
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from backend.app.config import JOBS_DIR

# In-memory registry of jobs
JOBS: Dict[str, Dict[str, Any]] = {}

def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    if job_id in JOBS:
        return JOBS[job_id]
    
    # Try reading from disk
    job_file = JOBS_DIR / f"{job_id}.json"
    if job_file.exists():
        try:
            with open(job_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                JOBS[job_id] = data
                return data
        except Exception:
            return None
    return None

def save_job(job_id: str, data: Dict[str, Any]):
    JOBS[job_id] = data
    job_file = JOBS_DIR / f"{job_id}.json"
    try:
        with open(job_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

async def _simulate_run_background(job_id: str):
    """Executes or mocks Bayesian MCMC sampling steps in the background."""
    save_job(job_id, {
        "job_id": job_id,
        "status": "running",
        "progress_percent": 15,
        "current_stage": "Loading observation data and meteorology priors...",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "finished_at": None,
        "result_dataset_id": None,
        "error": None
    })
    
    await asyncio.sleep(0.3)
    
    save_job(job_id, {
        "job_id": job_id,
        "status": "running",
        "progress_percent": 50,
        "current_stage": "Running NumPyro NUTS MCMC (sampling 4 chains)...",
        "started_at": JOBS[job_id]["started_at"],
        "finished_at": None,
        "result_dataset_id": None,
        "error": None
    })
    
    await asyncio.sleep(0.3)

    save_job(job_id, {
        "job_id": job_id,
        "status": "running",
        "progress_percent": 85,
        "current_stage": "Computing GEMM health burden & credible intervals...",
        "started_at": JOBS[job_id]["started_at"],
        "finished_at": None,
        "result_dataset_id": None,
        "error": None
    })
    
    await asyncio.sleep(0.2)

    save_job(job_id, {
        "job_id": job_id,
        "status": "completed",
        "progress_percent": 100,
        "current_stage": "MCMC inference and health propagation complete.",
        "started_at": JOBS[job_id]["started_at"],
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "result_dataset_id": "demo",
        "error": None
    })

async def start_job(job_type: str, config: Optional[Dict[str, Any]] = None) -> str:
    now_str = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    job_id = f"job_{now_str}_{uuid.uuid4().hex[:6]}"
    initial_record = {
        "job_id": job_id,
        "status": "queued",
        "progress_percent": 0,
        "current_stage": "Job queued in background worker...",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "finished_at": None,
        "result_dataset_id": None,
        "error": None
    }
    save_job(job_id, initial_record)
    asyncio.create_task(_simulate_run_background(job_id))
    return job_id
