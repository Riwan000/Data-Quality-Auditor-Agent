from typing import Dict, List
from pydantic import BaseModel

class AuditIssues(BaseModel):
    missingness: Dict[str, float]
    low_variance: List[str]
    skewed_features: List[str]
    leakage_risk: List[str]

class AuditResponse(BaseModel):
    dataset_shape: tuple
    risk_score: int
    risk_level: str
    issues: AuditIssues
    explanation: str
