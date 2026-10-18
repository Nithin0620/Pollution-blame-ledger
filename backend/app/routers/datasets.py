import os
import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from backend.app.config import OUTPUTS_DIR
from backend.app.schemas.dataset import DatasetSummary, DatasetDetail

router = APIRouter(prefix="/api/datasets", tags=["datasets"])

BLURBS = {
    "demo": "A simulated Delhi episode where the true answer is known. The safe place to see how the method works and how well it does.",
    "real_before": "Quiet period before the crop-burning season: low smog and little fire activity.",
    "real_peak": "The worst of the 2018 crop-burning season, including Diwali (7 Nov).",
    "real_after": "The fires have faded but smog stays high: winter stagnation."
}

def load_validation() -> Optional[dict]:
    val_path = OUTPUTS_DIR / "validation.json"
    if val_path.exists():
        try:
            with open(val_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def load_all_datasets():
    ds = []
    # 1. Synthetic demo
    rp = OUTPUTS_DIR / "results.json"
    if rp.exists():
        try:
            with open(rp, "r", encoding="utf-8") as f:
                res = json.load(f)
            ds.append({
                "id": "demo",
                "name": "Synthetic demo (known truth)",
                "kind": "synthetic",
                "results": res
            })
        except Exception as e:
            pass
            
    # 2. Real datasets
    dd = OUTPUTS_DIR / "datasets"
    if dd.is_dir():
        order = {"real_before": 0, "real_peak": 1, "real_after": 2}
        files = sorted(os.listdir(dd), key=lambda x: order.get(x[:-5], 9))
        for f in files:
            if f.endswith(".json"):
                ds_id = f[:-5]
                try:
                    with open(dd / f, "r", encoding="utf-8") as fp:
                        j = json.load(fp)
                    name = j.pop("_name", ds_id)
                    ds.append({
                        "id": ds_id,
                        "name": name,
                        "kind": "real",
                        "results": j
                    })
                except Exception:
                    pass
    return ds

@router.get("", response_model=List[DatasetSummary])
def list_datasets():
    all_ds = load_all_datasets()
    summaries = []
    for d in all_ds:
        res = d["results"]
        components = res.get("components", [])
        top_comp = max(components, key=lambda c: c["share"]["mean"]) if components else None
        
        summaries.append(DatasetSummary(
            id=d["id"],
            name=d["name"],
            kind=d["kind"],
            total_pm25_mean=res.get("total_pm25", {}).get("mean", 0.0),
            stations_count=len(res.get("stations", [])),
            dominant_source=top_comp["id"] if top_comp else "unknown",
            dominant_source_share=top_comp["share"]["mean"] if top_comp else 0.0,
            description=BLURBS.get(d["id"], "")
        ))
    return summaries

@router.get("/{dataset_id}", response_model=DatasetDetail)
def get_dataset(dataset_id: str):
    all_ds = load_all_datasets()
    target = next((d for d in all_ds if d["id"] == dataset_id), None)
    if not target:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found")
    
    val = load_validation()
    return DatasetDetail(
        id=target["id"],
        name=target["name"],
        kind=target["kind"],
        results=target["results"],
        validation=val if target["kind"] == "synthetic" else None
    )
