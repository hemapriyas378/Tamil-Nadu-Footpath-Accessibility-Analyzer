
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

FILE = (
    BASE_DIR / "data" / "processed"
    / "tn_footpath_accessibility_cleaned.csv"
)

if not FILE.exists():
    raise FileNotFoundError(f"Dataset not found: {FILE}")

df = pd.read_csv(FILE)

print("\nTAMIL NADU FOOTPATH DATA QUALITY AUDIT")
print("=" * 55)

print("Total records:", len(df))
print("Total columns:", len(df.columns))
print("Districts:", df["district"].nunique())

expected_districts = 38
actual_districts = df["district"].nunique()

print(
    "District coverage:",
    "PASS" if actual_districts == expected_districts else "CHECK"
)

print("\nMISSING VALUES")
print("-" * 55)
print(df.isna().sum().to_string())

print("\nDUPLICATE SOURCE IDs")
print("-" * 55)

if "source_record_id" in df.columns:
    print(df["source_record_id"].duplicated().sum())
else:
    print("source_record_id column not found")

print("\nCOORDINATE VALIDATION")
print("-" * 55)

for column in ["latitude", "longitude"]:
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    else:
        print(f"Missing column: {column}")

if {"latitude", "longitude"}.issubset(df.columns):
    invalid = (
        df["latitude"].isna()
        | df["longitude"].isna()
        | ~df["latitude"].between(8, 14)
        | ~df["longitude"].between(76, 81)
    )

    print("Invalid coordinate records:", int(invalid.sum()))

print("\nFEATURE DISTRIBUTION")
print("-" * 55)
print(df["feature_type"].value_counts().to_string())

print("\nAUDIT COMPLETED")
