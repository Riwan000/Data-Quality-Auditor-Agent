## Data Quality Auditor Agent

A lightweight data quality auditing service for CSV datasets, with optional data drift detection and natural-language explanations powered by an LLM.

## What this does

This project inspects a dataset before model training and reports risks such as missing values, low variance features, skewed numeric distributions, potential label leakage, and numeric drift compared to a baseline dataset.

## Architecture

```mermaid
flowchart LR
    subgraph Client
        A[CSV Upload / Local Script]
    end

    subgraph API
        B[FastAPI /audit]
        C[app.services.run_audit]
    end

    subgraph Auditor Core
        D[auditor.checks.run_checks]
        E[auditor.report.build_report]
        F[auditor.drift.detect_drift]
        G[auditor.report.add_drift_to_report]
        H[auditor.explain.explain_report]
    end

    subgraph Data
        I[Baseline CSV (optional)]
        J[Incoming CSV]
    end

    A --> B
    B --> C
    C --> D --> E
    C -->|baseline provided| F --> G
    C -->|explain=true| H
    I --> F
    J --> D
    E --> C
    G --> C
    H --> C
```

Above flow shows the FastAPI endpoint calling the audit pipeline. Checks generate issues, the report aggregates risk, drift is optionally injected, and the explanation is optionally generated using an LLM.

## Project structure

- `app/api.py`: FastAPI app and `/audit` endpoint. Validates CSV inputs, enforces size limits, and returns the audit response.
- `app/services.py`: Orchestrates the audit pipeline (`run_audit`).
- `app/schemas.py`: Pydantic response models returned by the API.
- `auditor/checks.py`: Core data quality checks (missingness, low variance, skewness, leakage risk).
- `auditor/report.py`: Risk scoring, report assembly, and drift risk adjustment.
- `auditor/drift.py`: Numeric drift detection using the KS test.
- `auditor/explain.py`: LLM prompt creation and OpenRouter API call for explanation.
- `auditor/baseline.py`: Utility script to compute a numeric baseline and save `baseline.json`.
- `data/`: Sample CSVs for baseline and incoming data.
- `main.py`: Local script example that runs the audit without the API.

## How the audit works (step-by-step)

1. **Load dataset**  
   The API or script reads the CSV into a Polars `DataFrame`.
2. **Run checks** (`auditor.checks.run_checks`)  
   - Missingness per column  
   - Low variance (unique ratio < 1%)  
   - Skewed numeric features (|skew| > 2)  
   - Leakage risk (column names containing target/label/outcome)
3. **Build report** (`auditor.report.build_report`)  
   Computes a weighted risk score and assigns `LOW`, `MEDIUM`, or `HIGH`.
4. **Detect drift (optional)** (`auditor.drift.detect_drift`)  
   If a baseline is provided, a KS test compares numeric distributions.
5. **Update report with drift** (`auditor.report.add_drift_to_report`)  
   Drift raises risk and adds `drifted_features`.
6. **Explain (optional)** (`auditor.explain.explain_report`)  
   Uses OpenRouter if configured, otherwise returns a placeholder.

## Risk scoring logic

The report uses weighted counts of issue types:

- Missingness: +3 per column with > 20% missing values
- Low variance: +1 per low-variance feature
- Skewed features: +2 per skewed numeric feature
- Leakage risk: +5 per suspicious column name
- Drift: +4 if any drift is detected (and risk level becomes HIGH)

Risk levels are derived from the total:

- `LOW`: 0–3
- `MEDIUM`: 4–7
- `HIGH`: 8+

## API usage

### Start the API

Use a typical FastAPI runner (e.g., uvicorn):

```
uvicorn app.api:app --reload
```

### Request

`POST /audit` with:

- `file` (required): CSV dataset to audit
- `baseline_file` (optional): CSV baseline dataset for drift detection
- `explain` (optional query param, default `true`): include explanation

### Example curl

```
curl -X POST "http://127.0.0.1:8000/audit?explain=true" ^
  -F "file=@data/incoming_drifted.csv" ^
  -F "baseline_file=@data/baseline.csv"
```

### Response shape

The response matches `AuditResponse`:

- `dataset_shape`: tuple of (rows, columns)
- `risk_score`: numeric risk score
- `risk_level`: `LOW` / `MEDIUM` / `HIGH`
- `issues`: detailed issue lists
- `explanation`: plain text explanation (LLM or placeholder)

## Local script usage

`main.py` reads sample CSVs and runs the same audit pipeline locally.

```
python main.py
```

## Baseline generation

`auditor/baseline.py` computes a simple baseline (mean and std for numeric columns) and writes `baseline.json`.

```
python auditor/baseline.py
```

## LLM explanation configuration

The explanation uses OpenRouter when these environment variables are set:

- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL`

If they are missing, the API returns `"LLM explanation placeholder."`.

## Dependencies

Key libraries:

- `fastapi` for the API
- `polars` for data loading/processing
- `scipy` for skewness and KS-test
- `pydantic` for response schemas
- `python-dotenv` for env loading

## Notes and limits

- Only CSV files are supported by the API.
- The API rejects datasets larger than 1,000,000 rows.
- Drift detection uses numeric columns present in the baseline.
