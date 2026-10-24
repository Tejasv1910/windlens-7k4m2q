
import json
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

MATCHED_FILE = DATA_DIR / "matched_jan_2026.csv"
METRICS_FILE = DATA_DIR / "metrics_jan_2026.json"

app = FastAPI(
    title="WindLens API",
    description="UK wind generation forecast analysis for January 2026",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_matched_data():
    if not MATCHED_FILE.exists():
        raise HTTPException(
            status_code=503,
            detail="Analysis data not found. Run analyze_january.py first.",
        )

    return pd.read_csv(MATCHED_FILE)


def load_metrics():
    if not METRICS_FILE.exists():
        raise HTTPException(
            status_code=503,
            detail="Metrics not found. Run analyze_january.py first.",
        )

    with open(METRICS_FILE, encoding="utf-8") as file:
        return json.load(file)


@app.get("/")
def root():
    return {
        "message": "Welcome to WindLens API",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "windlens-api"}


@app.get("/api/overview")
def overview():
    return load_metrics()


@app.get("/api/series")
def series(
    limit: int = Query(default=744, ge=1, le=744),
):
    df = load_matched_data()
    df["startTime"] = pd.to_datetime(df["startTime"], utc=True)
    df = df.sort_values("startTime").head(limit)

    columns = [
        "startTime",
        "forecast_mw",
        "actual_mw",
        "error_mw",
    ]

    records = df[columns].copy()
    records["startTime"] = records["startTime"].map(
        lambda value: value.isoformat()
    )

    return {"count": len(records), "data": records.to_dict("records")}


@app.get("/api/periods")
def periods(
    limit: int = Query(default=10, ge=1, le=100),
):
    df = load_matched_data()
    df["startTime"] = pd.to_datetime(df["startTime"], utc=True)

    df["absolute_error_mw"] = df["error_mw"].abs()
    df = df.sort_values("absolute_error_mw", ascending=False).head(limit)

    columns = [
        "startTime",
        "forecast_mw",
        "actual_mw",
        "error_mw",
        "absolute_error_mw",
        "forecast_publish_time",
        "lead_hours",
    ]

    records = df[columns].copy()
    records["startTime"] = records["startTime"].map(
        lambda value: value.isoformat()
    )

    return {"count": len(records), "data": records.to_dict("records")}
