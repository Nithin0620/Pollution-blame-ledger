import io
import csv
from typing import List, Dict
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.app.schemas.upload import UploadValidationResponse, PreviewPoint

router = APIRouter(prefix="/api/upload", tags=["upload"])

REQUIRED_COLUMNS = {
    "PM2.5": ["pm2.5", "pm25", "pm2_5"],
    "PM10": ["pm10"],
    "NO2": ["no2"],
    "SO2": ["so2"],
    "CO": ["co"],
    "WS": ["ws", "wind_speed", "windspeed", "wind_ms"],
    "WD": ["wd", "wind_direction", "winddir", "wind_dir_deg"],
}

OPTIONAL_COLUMNS = {
    "SR": ["sr", "solar", "solarradiation"],
    "AT": ["at", "temp", "temperature"],
}

TIME_COLUMNS = ["year", "month", "day", "hour"]

def find_col_index(header: List[str], aliases: List[str]) -> int:
    header_clean = [h.strip().lower().replace(" ", "").replace("_", "") for h in header]
    for alias in aliases:
        a_clean = alias.lower().replace(" ", "").replace("_", "")
        if a_clean in header_clean:
            return header_clean.index(a_clean)
    return -1

@router.post("/validate", response_model=UploadValidationResponse)
async def validate_csv(file: UploadFile = File(...)):
    if not file.filename.endswith((".csv", ".txt")):
        raise HTTPException(status_code=400, detail="Only CSV text files are accepted.")

    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    reader = csv.reader(io.StringIO(text))
    try:
        header = next(reader)
    except StopIteration:
        return UploadValidationResponse(
            valid=False,
            filename=file.filename,
            row_count=0,
            columns_present=[],
            columns_missing=list(REQUIRED_COLUMNS.keys()) + ["time_columns"],
            columns_optional=[],
            message="CSV file is empty."
        )

    cols_present = []
    cols_missing = []
    pm25_idx = -1

    for std_name, aliases in REQUIRED_COLUMNS.items():
        idx = find_col_index(header, [std_name] + aliases)
        if idx >= 0:
            cols_present.append(std_name)
            if std_name == "PM2.5":
                pm25_idx = idx
        else:
            cols_missing.append(std_name)

    # Check time columns
    has_time = all(find_col_index(header, [tc]) >= 0 for tc in TIME_COLUMNS)
    if not has_time:
        # Check single datetime column
        if find_col_index(header, ["datetime", "date", "timestamp"]) < 0:
            cols_missing.append("Date & Hour (year, month, day, hour)")

    cols_optional = []
    for opt_name, aliases in OPTIONAL_COLUMNS.items():
        if find_col_index(header, [opt_name] + aliases) >= 0:
            cols_optional.append(opt_name)

    # Read rows
    row_count = 0
    pm25_values = []
    for row in reader:
        if not row or all(c.strip() == "" for c in row):
            continue
        row_count += 1
        if pm25_idx >= 0 and pm25_idx < len(row):
            val_str = row[pm25_idx].strip()
            try:
                val = float(val_str)
                if val >= 0:
                    pm25_values.append(val)
                else:
                    pm25_values.append(None)
            except ValueError:
                pm25_values.append(None)

    valid = len(cols_missing) == 0 and row_count > 0
    good_pm = [v for v in pm25_values if v is not None]
    missing_pct = round(100.0 * (1.0 - len(good_pm) / max(row_count, 1)), 1) if row_count > 0 else 100.0
    mean_pm = round(sum(good_pm) / len(good_pm), 1) if good_pm else None
    max_pm = round(max(good_pm), 1) if good_pm else None

    # Generate up to 48 preview points
    preview_points = []
    if good_pm:
        sample_step = max(1, len(pm25_values) // 48)
        for i in range(0, min(len(pm25_values), sample_step * 48), sample_step):
            preview_points.append(PreviewPoint(hour=i, pm25=pm25_values[i]))

    msg = "Valid CSV ready for Bayesian receptor attribution." if valid else f"Missing required columns: {', '.join(cols_missing)}"

    return UploadValidationResponse(
        valid=valid,
        filename=file.filename,
        row_count=row_count,
        columns_present=cols_present,
        columns_missing=cols_missing,
        columns_optional=cols_optional,
        missing_percentage_pm25=missing_pct,
        mean_pm25=mean_pm,
        max_pm25=max_pm,
        preview_points=preview_points,
        message=msg
    )
