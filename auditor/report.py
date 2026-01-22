from typing import Dict

RISK_WEIGHTS = {
    "leakage_risk": 5,
    "missingness": 3,
    "skewed_features": 2,
    "low_variance": 1,
}

def build_report(df, checks: Dict) -> Dict:
    risk_score = 0
    issues = {}

    # Missingness
    high_missing = {
        k: v for k, v in checks["missingness"].items()
        if v > 0.2
    }
    if high_missing:
        risk_score += RISK_WEIGHTS["missingness"] * len(high_missing)
        issues["missingness"] = high_missing
    else:
        issues["missingness"] = {}

    # Low variance
    if checks["low_variance"]:
        risk_score += RISK_WEIGHTS["low_variance"] * len(checks["low_variance"])
    issues["low_variance"] = checks["low_variance"]

    # Skew
    if checks["skewed_features"]:
        risk_score += RISK_WEIGHTS["skewed_features"] * len(checks["skewed_features"])
    issues["skewed_features"] = checks["skewed_features"]

    # Leakage
    if checks["leakage_risk"]:
        risk_score += RISK_WEIGHTS["leakage_risk"] * len(checks["leakage_risk"])
    issues["leakage_risk"] = checks["leakage_risk"]

    # Risk level
    if risk_score >= 8:
        risk_level = "HIGH"
    elif risk_score >= 4:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "dataset_shape": df.shape,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "issues": issues,
    }

def add_drift_to_report(report: dict, drift_result: dict) -> dict:
    report["issues"]["drifted_features"] = drift_result.get(
        "drifted_features", []
    )

    if drift_result["drift_detected"]:
        report["risk_score"] += 4  # strong signal
        report["risk_level"] = "HIGH"

    return report
