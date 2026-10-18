from fastapi import APIRouter, HTTPException
from backend.app.schemas.simulation import SimulationRequest, SimulationResponse, SourceAverted
from backend.app.routers.datasets import load_all_datasets

router = APIRouter(prefix="/api/simulate", tags=["simulation"])

WHO_LIMIT = 15.0
CONTROLLABLE_SOURCES = ["traffic", "biomass", "dust", "industry"]

def calculate_averted(c: dict, fraction: float, quantile: str) -> float:
    d100 = c.get("deaths_100", {}).get(quantile, 0.0)
    d50 = c.get("deaths_50", {}).get(quantile, d100 * 0.5) if "deaths_50" in c else d100 * 0.5
    if fraction <= 0.5:
        return d50 * (fraction / 0.5)
    else:
        return d50 + (d100 - d50) * ((fraction - 0.5) / 0.5)

@router.post("/interventions", response_model=SimulationResponse)
def simulate_interventions(req: SimulationRequest):
    all_ds = load_all_datasets()
    dataset = next((d for d in all_ds if d["id"] == req.dataset_id), None)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset '{req.dataset_id}' not found")

    res = dataset["results"]
    components = {c["id"]: c for c in res.get("components", [])}
    original_pm25 = res.get("total_pm25", {}).get("mean", 0.0)
    total_deaths = res.get("total_deaths", {}).get("mean", 1.0)

    cuts_dict = {
        "traffic": req.cuts.traffic / 100.0,
        "biomass": req.cuts.biomass / 100.0,
        "dust": req.cuts.dust / 100.0,
        "industry": req.cuts.industry / 100.0,
    }

    averted_mean = 0.0
    averted_lo = 0.0
    averted_hi = 0.0
    pm_reduction = 0.0
    by_source = []

    for src in CONTROLLABLE_SOURCES:
        f = cuts_dict.get(src, 0.0)
        c = components.get(src)
        if not c:
            continue
        
        a_mean = calculate_averted(c, f, "mean")
        a_lo = calculate_averted(c, f, "lo")
        a_hi = calculate_averted(c, f, "hi")
        
        averted_mean += a_mean
        averted_lo += a_lo
        averted_hi += a_hi
        
        mean_ugm3 = c.get("mean_ugm3", {}).get("mean", 0.0)
        pm_reduction += mean_ugm3 * f
        by_source.append(SourceAverted(source=src, averted_deaths=round(a_mean, 2)))

    new_pm25 = max(0.0, original_pm25 - pm_reduction)
    abs_red = original_pm25 - new_pm25
    pct_red = (abs_red / original_pm25 * 100.0) if original_pm25 > 0 else 0.0

    # Identifiability warning for traffic vs biomass
    warning = None
    pairs = res.get("identifiability", {}).get("flagged_pairs", [])
    tb_pair = next((p for p in pairs if {"traffic", "biomass"}.issubset({p.get("a"), p.get("b")})), None)
    if tb_pair and (req.cuts.traffic > 0) != (req.cuts.biomass > 0):
        warning = "The data cannot separate vehicles from crop burning with full precision; only their combined sum is robust."

    return SimulationResponse(
        original_pm25=round(original_pm25, 1),
        new_pm25=round(new_pm25, 1),
        absolute_reduction=round(abs_red, 1),
        percentage_reduction=round(pct_red, 1),
        who_guideline=WHO_LIMIT,
        original_who_multiplier=round(original_pm25 / WHO_LIMIT, 1),
        new_who_multiplier=round(new_pm25 / WHO_LIMIT, 1),
        averted_deaths_mean=round(averted_mean, 1),
        averted_deaths_lo=round(averted_lo, 1),
        averted_deaths_hi=round(averted_hi, 1),
        averted_share_of_total=round((averted_mean / total_deaths) if total_deaths > 0 else 0.0, 3),
        by_source=by_source,
        identifiability_warning=warning
    )
