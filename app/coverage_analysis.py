
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

FILE = BASE_DIR / "data" / "processed" / "tn_footpath_accessibility_cleaned.csv"

df = pd.read_csv(FILE)

attributes = [
    "width",
    "surface",
    "wheelchair",
    "tactile_paving",
    "kerb",
    "sidewalk"
]

print("\nTAMIL NADU ACCESSIBILITY DATA COVERAGE")
print("=" * 55)

print("Total Records:", len(df))
print("Districts:", df["district"].nunique())

print("\nATTRIBUTE COVERAGE")
print("-" * 55)

for column in attributes:
    if column in df.columns:
        available = df[column].notna() & (
            df[column].astype(str).str.strip() != ""
        )
        count = int(available.sum())
        percentage = count / len(df) * 100 if len(df) else 0

        print(
            f"{column:20} {count:6} / {len(df):6} "
            f"({percentage:.2f}%)"
        )

print("\nDISTRICT-WISE COVERAGE")
print("-" * 55)

coverage = df.groupby("district")[attributes].apply(
    lambda group: group.notna().sum()
)

print(coverage.to_string())

output = BASE_DIR / "data" / "processed" / "attribute_coverage_by_district.csv"
coverage.to_csv(output)

print("\nReport saved:", output)
# Additional district-wise percentage coverage

district_records = df.groupby("district").size()

coverage_percent = coverage.div(
    district_records, axis=0
).mul(100).round(2)

coverage_percent.insert(
    0, "total_records", district_records
)

percentage_output = (
    BASE_DIR / "data" / "processed"
    / "district_attribute_coverage_percentage.csv"
)

coverage_percent.to_csv(percentage_output)

print("Percentage report saved:", percentage_output)