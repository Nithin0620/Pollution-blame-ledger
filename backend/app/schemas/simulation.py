from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class PolicyCuts(BaseModel):
    traffic: float = Field(default=0.0, ge=0.0, le=100.0)
    industry: float = Field(default=0.0, ge=0.0, le=100.0)
    dust: float = Field(default=0.0, ge=0.0, le=100.0)
    biomass: float = Field(default=0.0, ge=0.0, le=100.0)

class SimulationRequest(BaseModel):
    dataset_id: str
    cuts: PolicyCuts

class SourceAverted(BaseModel):
    source: str
    averted_deaths: float

class SimulationResponse(BaseModel):
    original_pm25: float
    new_pm25: float
    absolute_reduction: float
    percentage_reduction: float
    who_guideline: float = 15.0
    original_who_multiplier: float
    new_who_multiplier: float
    averted_deaths_mean: float
    averted_deaths_lo: float
    averted_deaths_hi: float
    averted_share_of_total: float
    by_source: List[SourceAverted]
    identifiability_warning: Optional[str] = None
