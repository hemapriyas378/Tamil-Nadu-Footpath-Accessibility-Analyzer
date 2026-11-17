from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "processed" / "tn_accessibility_scored.csv"

TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="Tamil Nadu Footpath Accessibility Analyzer",
    description="District-wise footpath accessibility evidence analysis",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def load_dataset():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}. "
            "Run accessibility_scoring.py first."
        )

    df = pd.read_csv(DATA_FILE)

    # Convert missing values to JSON-compatible None
    df = df.astype(object).where(pd.notna(df), None)

    return df


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.get("/api/health")
async def health():
    return {
        "status": "running",
        "project": "Tamil Nadu Footpath Accessibility Analyzer"
    }


@app.get("/api/summary")
async def summary():
    try:
        df = load_dataset()

        return {
            "total_records": len(df),
            "district_count": (
                int(df["district"].nunique())
                if "district" in df.columns else 0
            ),
            "feature_distribution": (
                df["feature_type"].value_counts().to_dict()
                if "feature_type" in df.columns else {}
            ),
            "available_columns": df.columns.tolist()
        }

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/api/districts")
async def districts():
    try:
        df = load_dataset()

        if "district" not in df.columns:
            return {"districts": []}

        return {
            "districts": sorted(
                df["district"].dropna().unique().tolist()
            )
        }

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/api/records")
async def records(
    district: str | None = Query(default=None),
    feature_type: str | None = Query(default=None),
    limit: int = Query(default=5000, ge=1, le=20000)
):
    try:
        df = load_dataset()

        if district and "district" in df.columns:
            df = df[
                df["district"].astype(str).str.lower()
                == district.lower()
            ]

        if feature_type and "feature_type" in df.columns:
            df = df[
                df["feature_type"].astype(str).str.lower()
                == feature_type.lower()
            ]

        df = df.head(limit)

        records_data = df.to_dict(orient="records")

        return {
            "count": len(records_data),
            "records": records_data
        }

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))



@app.get("/api/district-summary")
async def district_summary():
    try:
        df = load_dataset()

        required = {
            "district",
            "accessibility_evidence_score",
            "attribute_coverage_pct"
        }

        if not required.issubset(df.columns):
            raise HTTPException(
                status_code=400,
                detail="Required scoring columns are missing."
            )

        # Convert scoring columns back to numeric
        df["accessibility_evidence_score"] = pd.to_numeric(
            df["accessibility_evidence_score"],
            errors="coerce"
        )

        df["attribute_coverage_pct"] = pd.to_numeric(
            df["attribute_coverage_pct"],
            errors="coerce"
        )

        result = (
            df.groupby("district", dropna=True)
            .agg(
                record_count=("district", "size"),
                average_evidence_score=(
                    "accessibility_evidence_score", "mean"
                ),
                average_attribute_coverage=(
                    "attribute_coverage_pct", "mean"
                )
            )
            .reset_index()
            .sort_values("district")
        )

        result = result.round(2)

        # Convert missing numeric results to JSON-compatible None
        result = result.astype(object).where(
            pd.notna(result), None
        )

        return result.to_dict(orient="records")

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

    
@app.get("/api/coverage")
async def coverage():
    try:
        coverage_file = (
            BASE_DIR / "data" / "processed"
            / "district_attribute_coverage_percentage.csv"
        )

        if not coverage_file.exists():
            raise FileNotFoundError(
                "District coverage percentage report not found."
            )

        df = pd.read_csv(coverage_file)
        df = df.astype(object).where(pd.notna(df), None)

        return df.to_dict(orient="records")

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
