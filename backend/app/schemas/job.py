from typing import Optional, Dict, Any
from pydantic import BaseModel

class JobRunRequest(BaseModel):
    type: str = "demo"
    config: Optional[Dict[str, Any]] = None

class JobStatusResponse(BaseModel):
    job_id: str
    status: str  # queued, running, completed, failed
    progress_percent: int
    current_stage: str
    started_at: str
    finished_at: Optional[str] = None
    result_dataset_id: Optional[str] = None
    error: Optional[str] = None
