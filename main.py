import polars as pl
from app.services import run_audit

baseline_df = pl.read_csv("data/baseline.csv")
df = pl.read_csv("data/incoming_drifted.csv")
explain = True
report, explanation = run_audit(
    df,
    explain=explain,
    baseline_df=baseline_df
)
print(report)
print(explanation)