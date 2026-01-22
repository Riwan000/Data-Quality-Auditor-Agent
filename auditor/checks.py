import polars as pl 
from typing import Dict, List
from scipy.stats import skew

def run_checks(df: pl.DataFrame) -> Dict[str, float]:
    checks = {}

    missingness = {
        col : (df.select(pl.col(col).null_count())[0, 0] / df.height)
        for col in df.columns
    }

    checks['missingness'] = missingness

    low_variance = [
        col
        for col in df.columns
        if (df.select(pl.col(col).n_unique())[0, 0] / df.height) < 0.01
    ]
    checks['low_variance'] = low_variance

    numeric_cols = [
        col for col, dtype in zip(df.columns, df.dtypes)
        if dtype in [pl.Float64, pl.Int64]
    ]

    skewed_features = []
    for col in numeric_cols:
        values = (
            df.select(col)
                .drop_nulls()
                .to_numpy()
                .flatten()
        )
        if len(values) > 0 and abs(skew(values)) > 2:
            skewed_features.append(col)

    checks['skewed_features'] = skewed_features

    leakage_risk = [
        col for col in df.columns
        if any(x in col.lower() for x in ['target', 'label', 'outcome'])
    ]

    checks['leakage_risk'] = leakage_risk

    return checks


if __name__ == '__main__':
    df = pl.read_csv('data/sample1.csv')
    checks = run_checks(df)
    print(checks)