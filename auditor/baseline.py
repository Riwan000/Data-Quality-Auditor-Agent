import polars as pl
from typing import List
import json

try:
    from auditor.drift import get_numeric_columns
except ModuleNotFoundError:
    # Allow running as a standalone script (python auditor/baseline.py)
    from drift import get_numeric_columns

def compute_baseline(df: pl.DataFrame) -> dict:
    numeric_cols = get_numeric_columns(df)

    baseline = {}
    for col in numeric_cols:
        baseline[col] = {
            "mean": df.select(pl.col(col).mean())[0, 0],
            "std": df.select(pl.col(col).std())[0, 0]
        }

    return baseline

df = pl.read_csv('data/sample1.csv')
baseline = compute_baseline(df)
with open("baseline.json", "w") as f:
    json.dump(baseline, f, indent=2)
