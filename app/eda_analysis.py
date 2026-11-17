
import csv
from pathlib import Path
from collections import Counter, defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "tn_footpath_accessibility_cleaned.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed"

DISTRICT_REPORT = OUTPUT_DIR / "district_feature_summary.csv"
ATTRIBUTE_REPORT = OUTPUT_DIR / "attribute_coverage_report.csv"
SUMMARY_REPORT = OUTPUT_DIR / "eda_summary.txt"

ATTRIBUTES = [
    "width",
    "surface",
    "wheelchair",
    "tactile_paving",
    "kerb"
]


def run_eda():

    if not INPUT_FILE.exists():
        print("ERROR: Cleaned dataset not found!")
        return

    with open(INPUT_FILE, encoding="utf-8-sig") as file:
        records = list(csv.DictReader(file))

    if not records:
        print("Dataset is empty!")
        return

    districts = defaultdict(Counter)
    features = Counter()
    attribute_counts = Counter()

    for row in records:

        district = row.get("district", "Unknown")
        feature = row.get("feature_type", "Unknown")

        districts[district][feature] += 1
        features[feature] += 1

        for attribute in ATTRIBUTES:
            if row.get(attribute, "").strip():
                attribute_counts[attribute] += 1

    # District-wise report
    with open(
        DISTRICT_REPORT,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "district",
            "total_records",
            "footway",
            "sidewalk",
            "crossing"
        ])

        for district in sorted(districts):

            counts = districts[district]

            writer.writerow([
                district,
                sum(counts.values()),
                counts["footway"],
                counts["sidewalk"],
                counts["crossing"]
            ])

    # Attribute coverage report
    with open(
        ATTRIBUTE_REPORT,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "attribute",
            "available_records",
            "missing_records",
            "coverage_percentage"
        ])

        for attribute in ATTRIBUTES:

            available = attribute_counts[attribute]
            missing = len(records) - available

            percentage = (
                available / len(records)
            ) * 100

            writer.writerow([
                attribute,
                available,
                missing,
                round(percentage, 2)
            ])

    # Text summary
    with open(
        SUMMARY_REPORT,
        "w",
        encoding="utf-8"
    ) as file:

        file.write("TAMIL NADU FOOTPATH ACCESSIBILITY - EDA\n")
        file.write("=" * 50 + "\n\n")

        file.write(f"Total records: {len(records)}\n")
        file.write(
            f"Districts: {len(districts)}\n\n"
        )

        file.write("FEATURE DISTRIBUTION\n")
        file.write("-" * 30 + "\n")

        for feature, count in features.items():
            file.write(f"{feature}: {count}\n")

        file.write("\nDISTRICT RECORD COUNTS\n")
        file.write("-" * 30 + "\n")

        for district in sorted(districts):
            file.write(
                f"{district}: {sum(districts[district].values())}\n"
            )

        file.write("\nEDA COMPLETED\n")

    print("=" * 45)
    print("EDA ANALYSIS COMPLETED")
    print("=" * 45)

    print("Total records:", len(records))
    print("Districts:", len(districts))
    print("Feature categories:", dict(features))

    print("\nOUTPUT FILES")
    print(DISTRICT_REPORT)
    print(ATTRIBUTE_REPORT)
    print(SUMMARY_REPORT)


if __name__ == "__main__":
    run_eda()
