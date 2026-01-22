from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
import polars as pl

from app.services import run_audit
from app.schemas import AuditResponse

app = FastAPI(
    title="Data Quality Auditor",
    description="Audit datasets before training ML models",
    version="1.0"
)

@app.post("/audit", response_model=AuditResponse)
async def audit_dataset(
    file: UploadFile = File(...),
    baseline_file: Optional[UploadFile] = File(None),
    explain: bool = True
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files supported")

    try:
        df = pl.read_csv(file.file)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV file")

    baseline_df = None
    if baseline_file is not None:
        if not baseline_file.filename.endswith(".csv"):
            raise HTTPException(
                status_code=400,
                detail="Only CSV files supported for baseline"
            )

        try:
            baseline_df = pl.read_csv(baseline_file.file)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid baseline CSV file"
            )

    if df.height > 1_000_000:
        raise HTTPException(
            status_code=413,
            detail="Dataset too large for audit"
        )

    report, explanation = run_audit(
        df,
        explain=explain,
        baseline_df=baseline_df
    )

    return {
        **report,
        "explanation": explanation
    }
