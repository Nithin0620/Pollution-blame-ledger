from typing import List, Optional, Dict
from pydantic import BaseModel

class PreviewPoint(BaseModel):
    hour: int
    pm25: Optional[float] = None

class UploadValidationResponse(BaseModel):
    valid: bool
    filename: str
    row_count: int
    date_range: Optional[List[str]] = None
    columns_present: List[str]
    columns_missing: List[str]
    columns_optional: List[str]
    missing_percentage_pm25: Optional[float] = None
    mean_pm25: Optional[float] = None
    max_pm25: Optional[float] = None
    preview_points: List[PreviewPoint] = []
    message: str
