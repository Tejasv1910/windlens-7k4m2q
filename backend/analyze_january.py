
import json
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

ACTUALS_FILE = DATA_DIR / "actuals_jan_2026.csv"
FORECASTS_FILE = DATA_DIR / "forecasts_jan_2026.csv"

MATCHED_FILE = DATA_DIR / "matched_jan_2026.csv"
SUMMARY_FILE = DATA_DIR / "metrics_jan_2026.json"

# Prototype assumption: forecast must be available at least
# 12 hours before the delivery hour begins.
CUTOFF_HOURS = 12


def load_data():
    actuals = pd.read_csv(ACTUALS_FILE)
    forecasts = pd.read_csv(FORECASTS_FILE)

    for frame in (actuals, forecasts):
        frame["startTime"] = pd.to_datetime(
            frame["startTime"], utc=True
        )
        frame["publishTime"] = pd.to_datetime(
            frame["publishTime"], utc=True
        )
        frame["generation"] = pd.to_numeric(
            frame["generation"], errors="coerce"
        )

    actuals = actuals.dropna(
        subset=["startTime", "generation"]
    )
    forecasts = forecasts.dropna(
        subset=["startTime", "publishTime", "generation"]
    )

    return actuals, forecasts


def build_hourly_actuals(actuals):
    # FUELHH reports half-hourly wind generation.
    # Average the two readings within each UTC delivery hour.
    actuals = actuals.copy()
    actuals["hour"] = actuals["startTime"].dt.floor("h")

    hourly = (
        actuals.groupby("hour")
        .agg(
            actual_mw=("generation", "mean"),
            actual_half_hours=("generation", "count"),
        )
        .reset_index()
        .rename(columns={"hour": "startTime"})
    )

    # Exclude incomplete hours instead of silently treating
    # a single half-hour reading as a complete hourly average.
    hourly = hourly[hourly["actual_half_hours"] == 2].copy()

    return hourly


def select_forecasts(forecasts):
    selected = []

    # Each delivery hour may have many forecast versions.
    for delivery_time, group in forecasts.groupby("startTime"):
        cutoff_time = (
            delivery_time - pd.Timedelta(hours=CUTOFF_HOURS)
        )

        eligible = group[group["publishTime"] <= cutoff_time]

        if eligible.empty:
            continue

        # Most recently published forecast that meets the cutoff.
        chosen = eligible.sort_values("publishTime").iloc[-1]

        selected.append({
            "startTime": delivery_time,
            "forecast_mw": float(chosen["generation"]),
            "forecast_publish_time": chosen["publishTime"],
            "cutoff_time": cutoff_time,
            "lead_hours": (
                delivery_time - chosen["publishTime"]
            ).total_seconds() / 3600,
        })

    return pd.DataFrame(selected)


def main():
    actuals, forecasts = load_data()

    hourly_actuals = build_hourly_actuals(actuals)
    selected_forecasts = select_forecasts(forecasts)

    if selected_forecasts.empty:
        raise RuntimeError(
            "No forecasts met the publication cutoff. "
            "Check the publication window and cutoff assumption."
        )

    matched = hourly_actuals.merge(
        selected_forecasts,
        on="startTime",
        how="inner",
        validate="one_to_one",
    )

    if matched.empty:
        raise RuntimeError(
            "No forecast periods matched actual delivery hours."
        )

    # Positive error means the forecast was higher than actual.
    matched["error_mw"] = (
        matched["forecast_mw"] - matched["actual_mw"]
    )
    matched["absolute_error_mw"] = matched["error_mw"].abs()
    matched["squared_error_mw"] = matched["error_mw"] ** 2

    metrics = {
        "month": "2026-01",
        "cutoff_hours": CUTOFF_HOURS,
        "hourly_actual_periods": int(len(hourly_actuals)),
        "eligible_forecast_periods": int(len(selected_forecasts)),
        "matched_periods": int(len(matched)),
        "coverage_percent": round(
            100 * len(matched) / len(hourly_actuals), 2
        ),
        "mae_mw": round(
            float(matched["absolute_error_mw"].mean()), 2
        ),
        "rmse_mw": round(
            float(np.sqrt(matched["squared_error_mw"].mean())), 2
        ),
        "bias_mw": round(float(matched["error_mw"].mean()), 2),
        "mean_lead_hours": round(
            float(matched["lead_hours"].mean()), 2
        ),
        "underforecast_hours": int(
            (matched["error_mw"] < 0).sum()
        ),
        "overforecast_hours": int(
            (matched["error_mw"] > 0).sum()
        ),
    }

    # Save timestamps in ISO format for reliable CSV interchange.
    matched.to_csv(MATCHED_FILE, index=False)

    with open(SUMMARY_FILE, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)

    print("\nWindLens — January 2026 forecast accuracy")
    print("-" * 45)

    for key, value in metrics.items():
        print(f"{key}: {value}")

    print("\nSaved matched periods:", MATCHED_FILE)
    print("Saved metrics:", SUMMARY_FILE)


if __name__ == "__main__":
    main()
