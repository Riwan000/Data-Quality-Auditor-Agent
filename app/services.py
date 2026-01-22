from auditor.checks import run_checks
from auditor.report import build_report, add_drift_to_report
from auditor.explain import explain_report
from auditor.drift import detect_drift


def run_audit(
    df,
    explain: bool = True,
    baseline_df=None
):
    checks = run_checks(df)
    report = build_report(df, checks)

    if baseline_df is not None:
        drift_result = detect_drift(baseline_df, df)
        report = add_drift_to_report(report, drift_result)

    explanation = ""
    if explain:
        explanation = explain_report(report)

    return report, explanation
