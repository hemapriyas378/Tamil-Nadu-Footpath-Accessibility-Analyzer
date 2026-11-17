
import csv
from pathlib import Path
from collections import Counter, defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "tn_footpath_accessibility.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed"

CLEAN_FILE = OUTPUT_DIR / "tn_footpath_accessibility_cleaned.csv"
REJECTED_FILE = OUTPUT_DIR / "rejected_records.csv"
REPORT_FILE = OUTPUT_DIR / "cleaning_report.csv"

TN_BOUNDS = {
    "min_lat": 8.0,
    "max_lat": 14.0,
    "min_lon": 76.0,
    "max_lon": 81.0
}

ACCESSIBILITY_FIELDS = [
    "width",
    "surface",
    "wheelchair",
    "tactile_paving",
    "kerb"
]


def clean_value(value):
    if value is None:
        return ""
    return str(value).strip()


def validate_record(record):

    reasons = []

    # Check source ID
    source_id = record.get("source_record_id", "")

    if not source_id:
        reasons.append("missing_source_id")

    # Check district
    if not record.get("district", ""):
        reasons.append("missing_district")

    # Check feature type
    allowed_features = {
        "footway",
        "sidewalk",
        "crossing"
    }

    if record.get("feature_type") not in allowed_features:
        reasons.append("invalid_feature_type")

    # Check coordinates
    try:
        lat = float(record.get("latitude", ""))
        lon = float(record.get("longitude", ""))

        if not (
            TN_BOUNDS["min_lat"] <= lat <= TN_BOUNDS["max_lat"]
            and TN_BOUNDS["min_lon"] <= lon <= TN_BOUNDS["max_lon"]
        ):
            reasons.append("outside_tamil_nadu_bbox")

    except (ValueError, TypeError):
        reasons.append("missing_or_invalid_coordinates")

    return reasons


def main():

    print("=" * 55)
    print("TAMIL NADU DATASET CLEANING")
    print("=" * 55)

    if not INPUT_FILE.exists():
        print("ERROR: Input dataset not found!")
        print(INPUT_FILE)
        return

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        INPUT_FILE,
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        records = list(reader)

    if not fieldnames:
        print("ERROR: Dataset has no column headers.")
        return

    cleaned_records = []
    rejected_records = []

    seen_ids = set()

    stats = Counter()
    district_stats = defaultdict(Counter)

    stats["input_records"] = len(records)

    for record in records:

        # Normalize whitespace without inventing values.
        record = {
            key: clean_value(value)
            for key, value in record.items()
        }

        # Preserve blank accessibility attributes.
        for field in ACCESSIBILITY_FIELDS:
            record[field] = record.get(field, "")

        # Check data quality.
        reasons = validate_record(record)

        source_id = record.get("source_record_id", "")

        # Check duplicate source IDs.
        if source_id and source_id in seen_ids:
            reasons.append("duplicate_source_id")

        elif source_id:
            seen_ids.add(source_id)

        # Reject records with validation failures.
        if reasons:

            record["rejection_reason"] = ";".join(reasons)

            rejected_records.append(record)

            stats["rejected_records"] += 1

            for reason in reasons:
                stats[reason] += 1

            continue

        # Convert valid coordinates into numeric format.
        record["latitude"] = str(
            float(record["latitude"])
        )

        record["longitude"] = str(
            float(record["longitude"])
        )

        cleaned_records.append(record)

        stats["cleaned_records"] += 1

        district = record["district"]

        district_stats[district]["total"] += 1

        district_stats[district][
            record["feature_type"]
        ] += 1

        # Accessibility attribute coverage.
        for field in ACCESSIBILITY_FIELDS:

            if record[field]:
                stats[f"{field}_available"] += 1

            else:
                stats[f"{field}_missing"] += 1

    # ----------------------------------
    # SAVE CLEANED DATASET
    # ----------------------------------

    with open(
        CLEAN_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(cleaned_records)

    # ----------------------------------
    # SAVE REJECTED RECORDS
    # ----------------------------------

    rejected_fields = fieldnames + ["rejection_reason"]

    with open(
        REJECTED_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=rejected_fields
        )

        writer.writeheader()
        writer.writerows(rejected_records)

    # ----------------------------------
    # SAVE CLEANING REPORT
    # ----------------------------------

    report_fields = [
        "district",
        "total_records",
        "footway",
        "sidewalk",
        "crossing"
    ]

    with open(
        REPORT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=report_fields
        )

        writer.writeheader()

        for district in sorted(district_stats):

            item = district_stats[district]

            writer.writerow({
                "district": district,
                "total_records": item["total"],
                "footway": item["footway"],
                "sidewalk": item["sidewalk"],
                "crossing": item["crossing"]
            })

    # ----------------------------------
    # FINAL SUMMARY
    # ----------------------------------

    print("\nCLEANING SUMMARY")

    print("Input records:", stats["input_records"])
    print("Cleaned records:", len(cleaned_records))
    print("Rejected records:", len(rejected_records))

    print("\nREJECTION REASONS")

    for reason in [
        "missing_source_id",
        "missing_district",
        "invalid_feature_type",
        "outside_tamil_nadu_bbox",
        "missing_or_invalid_coordinates",
        "duplicate_source_id"
    ]:

        print(reason, ":", stats[reason])

    print("\nACCESSIBILITY ATTRIBUTE COVERAGE")

    for field in ACCESSIBILITY_FIELDS:

        available = stats[f"{field}_available"]
        missing = stats[f"{field}_missing"]

        print(
            f"{field}: {available} available, "
            f"{missing} missing"
        )

    print("\nDISTRICTS IN CLEANED DATA:", len(district_stats))

    print("\nOUTPUT FILES")

    print("Cleaned:", CLEAN_FILE)
    print("Rejected:", REJECTED_FILE)
    print("Report:", REPORT_FILE)

    print("\nDATASET CLEANING COMPLETED")


if __name__ == "__main__":
    main()
