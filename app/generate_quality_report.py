
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = (
    BASE_DIR / "data" / "processed"
    / "tn_footpath_accessibility_cleaned.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if not DATA_FILE.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

df = pd.read_csv(DATA_FILE)

# Dataset overview
total_records = len(df)
total_columns = len(df.columns)
total_districts = df["district"].nunique()

# Feature distribution
feature_counts = df["feature_type"].value_counts()

# Accessibility attributes
attributes = [
    "width",
    "surface",
    "wheelchair",
    "tactile_paving",
    "kerb",
    "sidewalk"
]

attribute_rows = []

for column in attributes:
    if column not in df.columns:
        continue

    known = int(df[column].notna().sum())
    missing = int(df[column].isna().sum())

    attribute_rows.append({
        "attribute": column,
        "known_records": known,
        "missing_records": missing,
        "coverage_percentage": round(
            (known / total_records * 100)
            if total_records else 0, 2
        )
    })

attribute_report = pd.DataFrame(attribute_rows)

# Duplicate validation
duplicate_count = (
    int(df["source_record_id"].duplicated().sum())
    if "source_record_id" in df.columns else None
)

# Coordinate validation
latitude = pd.to_numeric(df["latitude"], errors="coerce")
longitude = pd.to_numeric(df["longitude"], errors="coerce")

invalid_coordinates = (
    latitude.isna()
    | longitude.isna()
    | ~latitude.between(8, 14)
    | ~longitude.between(76, 81)
)

invalid_coordinate_count = int(invalid_coordinates.sum())

# Save CSV reports
attribute_report.to_csv(
    OUTPUT_DIR / "final_attribute_quality_report.csv",
    index=False
)

feature_counts.rename_axis("feature_type").reset_index(
    name="record_count"
).to_csv(
    OUTPUT_DIR / "final_feature_distribution_report.csv",
    index=False
)

# Generate text report
report = []

report.append("TAMIL NADU FOOTPATH ACCESSIBILITY ANALYZER")
report.append("FINAL DATA QUALITY REPORT")
report.append("=" * 60)

report.append("\n1. DATASET OVERVIEW")
report.append(f"Total records: {total_records}")
report.append(f"Total columns: {total_columns}")
report.append(f"Districts covered: {total_districts}/38")

report.append("\n2. FEATURE DISTRIBUTION")

for feature, count in feature_counts.items():
    report.append(f"{feature}: {count}")

report.append("\n3. ACCESSIBILITY ATTRIBUTE COVERAGE")
report.append(attribute_report.to_string(index=False))

report.append("\n4. DATA VALIDATION")
report.append(f"Duplicate source IDs: {duplicate_count}")
report.append(
    f"Invalid coordinates (broad bounding-box check): "
    f"{invalid_coordinate_count}"
)

report.append("\n5. DATA LIMITATIONS")
report.append(
    "- Missing accessibility attributes indicate unavailable "
    "mapped information, not confirmed inaccessibility."
)
report.append(
    "- Coordinate validation uses a broad Tamil Nadu bounding box, "
    "not exact district polygons."
)
report.append(
    "- OpenStreetMap records represent mapped infrastructure "
    "and are not a complete field survey."
)
report.append(
    "- Accessibility scores are evidence-based indicators, "
    "not certified accessibility assessments."
)
report.append(
    "- The dataset contains collected records only; "
    "no synthetic records were added."
)

report.append("\nEND OF REPORT")

report_text = "\n".join(report)

report_path = OUTPUT_DIR / "final_data_quality_report.txt"
report_path.write_text(report_text, encoding="utf-8")

print(report_text)

print("\nREPORTS GENERATED SUCCESSFULLY")
print("Saved:", report_path)
print("Saved:", OUTPUT_DIR / "final_attribute_quality_report.csv")
print("Saved:", OUTPUT_DIR / "final_feature_distribution_report.csv")
