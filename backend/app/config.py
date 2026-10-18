import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
DATA_DIR = BASE_DIR / "data"
JOBS_DIR = OUTPUTS_DIR / "jobs"

JOBS_DIR.mkdir(parents=True, exist_ok=True)
