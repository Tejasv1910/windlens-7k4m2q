
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

path = DATA_DIR / "matched_jan_2026.csv"
df = pd.read_csv(path)

for column in [
    "startTime",
    "forecast_publish_time",
    "cutoff_time",
]:
    df[column] = pd.to_datetime(df[column], utc=True)

print("Rows:", len(df))
print("Duplicate delivery hours:", df["startTime"].duplicated().sum())

# A forecast must have been published by the selected cutoff.
invalid = df["forecast_publish_time"] > df["cutoff_time"]
print("Forecasts published after cutoff:", int(invalid.sum()))

print("\nGeneration values (MW):")
print(df[["forecast_mw", "actual_mw"]].describe().round(2))

print("\nSelected forecast publication times:")
print("Distinct publication times:", df["forecast_publish_time"].nunique())
print("Earliest:", df["forecast_publish_time"].min())
print("Latest:  ", df["forecast_publish_time"].max())

print("\nSample matched periods:")
print(
    df[
        [
            "startTime",
            "forecast_mw",
            "actual_mw",
            "forecast_publish_time",
            "cutoff_time",
            "lead_hours",
            "error_mw",
        ]
    ].head(10).to_string(index=False)
)

print("\nValidation status:")
if len(df) != 744:
    print("CHECK: Expected 744 January hours.")
elif df["startTime"].duplicated().any():
    print("CHECK: Duplicate delivery hours found.")
elif invalid.any():
    print("CHECK: Some forecasts violate the cutoff.")
else:
    print("Basic timestamp and coverage checks passed.")
    print("Review value ranges and sample rows before publishing.")
