import polars as pl
from typing import List
from scipy.stats import ks_2samp

def get_numeric_columns(df: pl.DataFrame) -> List[str]:
    return [
        col for col, dtype in zip(df.columns, df.dtypes)
        if dtype in (pl.Int64, pl.Float64)
    ]


def detect_drift(
    baseline_df: pl.DataFrame,
    current_df: pl.DataFrame,
    p_threshold: float = 0.05
) -> dict:
    drifted_features = []

    numeric_cols = get_numeric_columns(baseline_df)

    for col in numeric_cols:
        base_vals = (
            baseline_df.select(col)
            .drop_nulls()
            .to_numpy()
            .flatten()
        )
        curr_vals = (
            current_df.select(col)
            .drop_nulls()
            .to_numpy()
            .flatten()
        )

        if len(base_vals) == 0 or len(curr_vals) == 0:
            continue

        _, p_value = ks_2samp(
            base_vals,
            curr_vals,
            method="asymp",
        )

        if p_value < p_threshold:
            drifted_features.append({
                "feature": col,
                "p_value": round(p_value, 5)
            })

    return {
        "drift_detected": len(drifted_features) > 0,
        "drifted_features": drifted_features
    }