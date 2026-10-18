from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class DatasetSummary(BaseModel):
    id: str
    name: str
    kind: str
    total_pm25_mean: float
    stations_count: int
    dominant_source: str
    dominant_source_share: float
    description: Optional[str] = None

class UncertaintyRange(BaseModel):
    mean: float
    lo: float
    hi: float

class ComponentShare(BaseModel):
    id: str
    share: UncertaintyRange
    ugm3: UncertaintyRange
    status: str
    deaths_100: Optional[UncertaintyRange] = None
    adm_100: Optional[UncertaintyRange] = None

class DatasetDetail(BaseModel):
    id: str
    name: str
    kind: str
    results: Dict[str, Any]
    validation: Optional[Dict[str, Any]] = None
