from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pathlib import Path
from app.models import Observation
from app.storage import init_db, add, get_all, count
from app.districts import TAMIL_NADU_DISTRICTS
from app.storage import init_db, add, get_all, count, get_district_coverage

app = FastAPI(title="Tamil Nadu Footpath Accessibility Analyzer", version="0.1.0")
@app.get("/api/districts")
def get_districts():
    return {
        "total_districts": len(TAMIL_NADU_DISTRICTS),
        "districts": TAMIL_NADU_DISTRICTS
    }
@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def home():
    return FileResponse(Path(__file__).resolve().parents[1] / "web" / "index.html")

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.1.0"}

@app.get("/api/observations")
def observations(limit: int = Query(500, ge=1, le=5000)):
    items = get_all(limit)
    return {"total_records": count(), "items": items}

@app.post("/api/observations", status_code=201)
def create_observation(item: Observation):
    try:
        return {"id": add(item), "message": "Record saved with provenance."}
    except Exception as e:
        raise HTTPException(status_code=409, detail=f"Could not save record: {e}")
@app.get("/api/district-coverage")
def district_coverage():
    coverage = get_district_coverage(TAMIL_NADU_DISTRICTS)

    return {
        "total_districts": len(coverage),
        "total_records": sum(
            item["total_records"] for item in coverage
        ),
        "district_coverage": coverage
    }