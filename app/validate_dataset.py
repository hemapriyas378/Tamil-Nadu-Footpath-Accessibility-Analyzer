
import csv
from pathlib import Path
from collections import Counter, defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent

FILE = (
    BASE_DIR / "data" / "processed"
    / "tn_footpath_accessibility.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed"

DISTRICT_REPORT = OUTPUT_DIR / "district_validation_report.csv"

EXPECTED_DISTRICTS = {
    "Ariyalur",
    "Chengalpattu",
    "Chennai",
    "Coimbatore",
    "Cuddalore",
    "Dharmapuri",
    "Dindigul",
    "Erode",
    "Kallakurichi",
    "Kancheepuram",
    "Karur",
    "Krishnagiri",
    "Madurai",
    "Mayiladuthurai",
    "Nagapattinam",
    "Namakkal",
    "The Nilgiris",
    "Perambalur",
    "Pudukkottai",
    "Ramanathapuram",
    "Ranipet",
    "Salem",
    "Sivaganga",
    "Tenkasi",
    "Thanjavur",
    "Theni",
    "Thoothukudi",
    "Tiruchirappalli",
    "Tirunelveli",
    "Tirupathur",
    "Tiruppur",
    "Tiruvallur",
    "Tiruvannamalai",
    "Tiruvarur",
    "Vellore",
    "Viluppuram",
    "Virudhunagar"
}


def validate():

    if not FILE.exists():
        print("ERROR: Consolidated dataset not found!")
        print(FILE)
        return

    with open(FILE, encoding="utf-8-sig") as file:
        records = list(csv.DictReader(file))

    total = len(records)

    if total == 0:
        print("ERROR: Dataset contains no records!")
        return

    # ---------------------------------
    # 1. ID VALIDATION
    # ---------------------------------

    ids = [
        r.get("source_record_id", "").strip()
        for r in records
    ]

    duplicates = len(ids) - len(set(ids))

    missing_ids = sum(not value for value in ids)

    # ---------------------------------
    # 2. COORDINATE VALIDATION
    # ---------------------------------

    missing_coordinates = 0
    invalid_coordinates = 0

    for r in records:

        lat_value = r.get("latitude", "").strip()
        lon_value = r.get("longitude", "").strip()

        if not lat_value or not lon_value:
            missing_coordinates += 1
            continue

        try:
            lat = float(lat_value)
            lon = float(lon_value)

            if not (
                8 <= lat <= 14
                and 76 <= lon <= 81
            ):
                invalid_coordinates += 1

        except (ValueError, TypeError):
            invalid_coordinates += 1

    # ---------------------------------
    # 3. DISTRICT VALIDATION
    # ---------------------------------

    district_counts = Counter(
        r.get("district", "").strip()
        for r in records
        if r.get("district", "").strip()
    )

    found_districts = set(district_counts.keys())

    missing_districts = (
        EXPECTED_DISTRICTS - found_districts
    )

    unexpected_districts = (
        found_districts - EXPECTED_DISTRICTS
    )

    # ---------------------------------
    # 4. FEATURE DISTRIBUTION
    # ---------------------------------

    feature_counts = Counter(
        r.get("feature_type", "").strip()
        for r in records
    )

    # ---------------------------------
    # 5. ACCESSIBILITY COVERAGE
    # ---------------------------------

    accessibility_fields = [
        "width",
        "surface",
        "wheelchair",
        "tactile_paving",
        "kerb"
    ]

    coverage = {}

    for field in accessibility_fields:

        available = sum(
            bool(r.get(field, "").strip())
            for r in records
        )

        coverage[field] = available

    # ---------------------------------
    # 6. DISTRICT-WISE FEATURE SUMMARY
    # ---------------------------------

    district_features = defaultdict(Counter)

    for r in records:

        district = r.get("district", "").strip()
        feature = r.get("feature_type", "").strip()

        district_features[district][feature] += 1

    # ---------------------------------
    # 7. SAVE DISTRICT REPORT
    # ---------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        DISTRICT_REPORT,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        fields = [
            "district",
            "total_records",
            "footway",
            "sidewalk",
            "crossing"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        writer.writeheader()

        for district in sorted(EXPECTED_DISTRICTS):

            features = district_features[district]

            writer.writerow({
                "district": district,
                "total_records": district_counts.get(
                    district, 0
                ),
                "footway": features.get("footway", 0),
                "sidewalk": features.get("sidewalk", 0),
                "crossing": features.get("crossing", 0)
            })

    # ---------------------------------
    # 8. FINAL VALIDATION REPORT
    # ---------------------------------

    print("\n" + "=" * 55)
    print("TAMIL NADU DATASET VALIDATION")
    print("=" * 55)

    print("\nGENERAL SUMMARY")

    print("Total records:", total)
    print("Expected districts:", len(EXPECTED_DISTRICTS))
    print("Districts found:", len(found_districts))
    print("Missing districts:", sorted(missing_districts))
    print("Unexpected districts:", sorted(unexpected_districts))

    print("\nID VALIDATION")

    print("Duplicate IDs:", duplicates)
    print("Missing IDs:", missing_ids)

    print("\nCOORDINATE VALIDATION")

    print("Missing coordinates:", missing_coordinates)
    print("Invalid coordinates:", invalid_coordinates)

    print("\nFEATURE DISTRIBUTION")

    for feature, count in sorted(feature_counts.items()):
        print(feature, ":", count)

    print("\nACCESSIBILITY ATTRIBUTE COVERAGE")

    for field, count in coverage.items():

        percentage = (count / total) * 100

        print(
            f"{field}: {count}/{total} "
            f"({percentage:.2f}%)"
        )

    print("\nDISTRICT-WISE RECORD COUNTS")

    for district in sorted(district_counts):

        print(
            district,
            ":",
            district_counts[district]
        )

    print("\nVALIDATION REPORT SAVED:")
    print(DISTRICT_REPORT)

    print("\n" + "=" * 55)
    print("VALIDATION FINISHED")
    print("=" * 55)


if __name__ == "__main__":
    validate()
