
from pathlib import Path

import httpx
import pandas as pd

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"

START = "2026-01-01T00:00:00Z"
END = "2026-02-01T00:00:00Z"

# Include a small buffer for actuals published after delivery starts.
ACTUALS_FROM = "2025-12-31T23:00:00Z"
ACTUALS_TO = "2026-02-01T01:00:00Z"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def fetch_records(client, path, params):
    url = f"{BASE_URL}{path}"
    response = client.get(url, params=params)
    print(f"GET {path}: HTTP {response.status_code}")
    response.raise_for_status()

    records = response.json()
    if not isinstance(records, list):
        raise ValueError(f"Unexpected response from {path}")

    print(f"  Retrieved {len(records)} records")
    return records


def in_january(series):
    dates = pd.to_datetime(series, utc=True, errors="coerce")
    return (
        (dates >= pd.Timestamp(START))
        & (dates < pd.Timestamp(END))
    )


def main():
    with httpx.Client(timeout=120.0) as client:
        actual_records = fetch_records(
            client,
            "/datasets/FUELHH/stream",
            {
                "publishDateTimeFrom": ACTUALS_FROM,
                "publishDateTimeTo": ACTUALS_TO,
            },
        )

        forecast_records = fetch_records(
            client,
            "/datasets/WINDFOR/stream",
           {
                "publishDateTimeFrom": "2025-12-30T00:00:00Z",
                "publishDateTimeTo": END,
            },
     )

    actuals = pd.DataFrame(actual_records)
    forecasts = pd.DataFrame(forecast_records)

    if actuals.empty or forecasts.empty:
        raise RuntimeError("One of the API responses was empty.")

    # Actual wind generation only.
    actuals = actuals[
        actuals["fuelType"].astype(str).str.upper() == "WIND"
    ].copy()

    # Keep January delivery periods, not merely January publication times.
    actuals = actuals[in_january(actuals["startTime"])].copy()
    forecasts = forecasts[in_january(forecasts["startTime"])].copy()

    for frame in (actuals, forecasts):
        frame["startTime"] = pd.to_datetime(
            frame["startTime"], utc=True, errors="coerce"
        )
        frame["publishTime"] = pd.to_datetime(
            frame["publishTime"], utc=True, errors="coerce"
        )
        frame["generation"] = pd.to_numeric(
            frame["generation"], errors="coerce"
        )

    actuals = actuals.dropna(
        subset=["startTime", "publishTime", "generation"]
    )
    forecasts = forecasts.dropna(
        subset=["startTime", "publishTime", "generation"]
    )

    actual_path = DATA_DIR / "actuals_jan_2026.csv"
    forecast_path = DATA_DIR / "forecasts_jan_2026.csv"

    actuals.to_csv(actual_path, index=False)
    forecasts.to_csv(forecast_path, index=False)

    print("\nDownload complete.")
    print("Actual wind rows:", len(actuals))
    print("Forecast rows:", len(forecasts))
    print("Distinct forecast publication times:",
          forecasts["publishTime"].nunique())

    if not actuals.empty:
        print("Actual delivery range:",
              actuals["startTime"].min(),
              "to", actuals["startTime"].max())

    if not forecasts.empty:
        print("Forecast delivery range:",
              forecasts["startTime"].min(),
              "to", forecasts["startTime"].max())

    print("\nSaved files:")
    print(actual_path)
    print(forecast_path)


if __name__ == "__main__":
    main()
