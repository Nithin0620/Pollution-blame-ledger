from fastapi import APIRouter, HTTPException
from backend.app.schemas.job import JobRunRequest, JobStatusResponse
from backend.app.services.job_runner import start_job, get_job

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.post("/run", response_model=JobStatusResponse)
async def run_job(req: JobRunRequest):
    job_id = await start_job(req.type, req.config)
    job_data = get_job(job_id)
    return JobStatusResponse(**job_data)

@router.get("/{job_id}", response_model=JobStatusResponse)
async def poll_job_status(job_id: str):
    job_data = get_job(job_id)
    if not job_data:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    return JobStatusResponse(**job_data)
