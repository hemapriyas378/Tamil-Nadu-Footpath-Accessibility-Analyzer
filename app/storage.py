import sqlite3
from pathlib import Path
from app.models import Observation

DB = Path(__file__).resolve().parents[1] / "data" / "observations.db"

def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with connect() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS observations (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          source_name TEXT NOT NULL, source_url TEXT NOT NULL,
          source_record_id TEXT NOT NULL, retrieved_on TEXT NOT NULL,
          district TEXT NOT NULL, feature_type TEXT NOT NULL,
          evidence_status TEXT NOT NULL, latitude REAL NOT NULL, longitude REAL NOT NULL,
          payload TEXT NOT NULL,
          UNIQUE(source_name, source_record_id)
        )
        """)

def add(item: Observation):
    d = item.model_dump(mode="json")
    with connect() as c:
        cur = c.execute(
            "INSERT INTO observations (source_name,source_url,source_record_id,retrieved_on,district,feature_type,evidence_status,latitude,longitude,payload) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (d["source_name"], d["source_url"], d["source_record_id"], d["retrieved_on"],
             d["district"], d["feature_type"], d["evidence_status"], d["latitude"],
             d["longitude"], __import__("json").dumps(d))
        )
        return cur.lastrowid

def get_all(limit=500):
    with connect() as c:
        rows = c.execute("SELECT payload FROM observations ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [__import__("json").loads(r["payload"]) for r in rows]

def count():
    with connect() as c:
        return c.execute("SELECT COUNT(*) FROM observations").fetchone()[0]

def get_district_coverage(districts):
    with connect() as c:
        rows = c.execute("""
            SELECT
                district,
                COUNT(*) AS total_records,
                SUM(
                    CASE WHEN evidence_status = 'field_verified'
                    THEN 1 ELSE 0 END
                ) AS verified_records
            FROM observations
            GROUP BY district
        """).fetchall()

    counts = {
        row["district"]: {
            "total_records": row["total_records"],
            "verified_records": row["verified_records"] or 0
        }
        for row in rows
    }

    return [
        {
            "district": district,
            "total_records": counts.get(district, {}).get("total_records", 0),
            "verified_records": counts.get(district, {}).get("verified_records", 0)
        }
        for district in districts
    ]
