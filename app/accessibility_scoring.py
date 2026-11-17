
import csv
from pathlib import Path
from collections import defaultdict
from datetime import date

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "tn_footpath_accessibility_cleaned.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed"

SCORED_FILE = OUTPUT_DIR / "tn_accessibility_scored.csv"
DISTRICT_FILE = OUTPUT_DIR / "district_accessibility_summary.csv"
METHOD_FILE = OUTPUT_DIR / "scoring_methodology.txt"


# Attribute weights (total = 100)
WEIGHTS = {
    "wheelchair": 30,
    "width": 20,
    "surface": 15,
    "kerb": 15,
    "tactile_paving": 10,
    "sidewalk": 10
}


def normalize(value):
    return str(value or "").strip().lower()


def parse_width(value):

    value = normalize(value)

    if not value:
        return None

    try:
        # Handle common units
        if "cm" in value:
            return float(value.replace("cm", "").strip()) / 100

        if "mm" in value:
            return float(value.replace("mm", "").strip()) / 1000

        if "m" in value:
            return float(value.replace("m", "").strip())

        return float(value)

    except ValueError:
        return None


def evaluate_wheelchair(value):

    value = normalize(value)

    if value in ["yes", "designated"]:
        return 100

    if value in ["limited", "permissive"]:
        return 60

    if value == "no":
        return 0

    return None


def evaluate_width(value):

    width = parse_width(value)

    if width is None:
        return None

    if width >= 1.5:
        return 100

    if width >= 1.2:
        return 70

    return 0


def evaluate_surface(value):

    value = normalize(value)

    if not value:
        return None

    good_surfaces = [
        "asphalt",
        "concrete",
        "paved",
        "paving_stones",
        "sett",
        "concrete:plates"
    ]

    poor_surfaces = [
        "gravel",
        "ground",
        "dirt",
        "earth",
        "mud",
        "sand"
    ]

    if value in good_surfaces:
        return 100

    if value in poor_surfaces:
        return 0

    return None


def evaluate_kerb(value):

    value = normalize(value)

    if not value:
        return None

    if value in ["lowered", "flush", "no", "rolled"]:
        return 100

    if value in ["raised", "high"]:
        return 0

    return None


def evaluate_tactile(value):

    value = normalize(value)

    if value in ["yes", "contrasted"]:
        return 100

    if value == "no":
        return 0

    return None


def evaluate_sidewalk(value):

    value = normalize(value)

    if value in ["yes", "both", "left", "right"]:
        return 100

    if value == "no":
        return 0

    return None


def calculate_score(record):

    results = {
        "wheelchair": evaluate_wheelchair(
            record.get("wheelchair")
        ),
        "width": evaluate_width(
            record.get("width")
        ),
        "surface": evaluate_surface(
            record.get("surface")
        ),
        "kerb": evaluate_kerb(
            record.get("kerb")
        ),
        "tactile_paving": evaluate_tactile(
            record.get("tactile_paving")
        ),
        "sidewalk": evaluate_sidewalk(
            record.get("sidewalk")
        )
    }

    available_weight = 0
    weighted_score = 0
    known_attributes = 0

    for attribute, score in results.items():

        if score is None:
            continue

        weight = WEIGHTS[attribute]

        available_weight += weight
        weighted_score += score * weight

        known_attributes += 1

    if available_weight == 0:
        evidence_score = ""
    else:
        evidence_score = round(
            weighted_score / available_weight, 2
        )

    coverage = round(
        (available_weight / sum(WEIGHTS.values())) * 100,
        2
    )

    if coverage < 30:
        evidence_level = "Insufficient evidence"

    elif coverage < 50:
        evidence_level = "Limited evidence"

    elif coverage < 75:
        evidence_level = "Moderate evidence"

    else:
        evidence_level = "Strong evidence coverage"

    return {
        "wheelchair_score": results["wheelchair"],
        "width_score": results["width"],
        "surface_score": results["surface"],
        "kerb_score": results["kerb"],
        "tactile_score": results["tactile_paving"],
        "sidewalk_score": results["sidewalk"],
        "accessibility_evidence_score": evidence_score,
        "known_attributes": known_attributes,
        "attribute_coverage_pct": coverage,
        "evidence_level": evidence_level
    }


def load_records():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_FILE}"
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)

        records = list(reader)

        required_columns = {
            "district",
            "feature_type",
            "wheelchair",
            "width",
            "surface",
            "kerb",
            "tactile_paving",
            "sidewalk"
        }

        missing = required_columns - set(
            reader.fieldnames or []
        )

        if missing:
            raise ValueError(
                f"Missing required columns: {sorted(missing)}"
            )

    return records


def generate_district_summary(records):

    districts = defaultdict(list)

    for record in records:
        districts[record["district"]].append(record)

    summary = []

    for district, district_records in sorted(
        districts.items()
    ):

        valid_scores = [
            float(r["accessibility_evidence_score"])
            for r in district_records
            if r["accessibility_evidence_score"] != ""
        ]

        coverages = [
            float(r["attribute_coverage_pct"])
            for r in district_records
        ]

        average_score = (
            round(sum(valid_scores) / len(valid_scores), 2)
            if valid_scores else ""
        )

        average_coverage = (
            round(sum(coverages) / len(coverages), 2)
            if coverages else 0
        )

        summary.append({
            "district": district,
            "total_records": len(district_records),
            "records_with_score": len(valid_scores),
            "average_evidence_score": average_score,
            "average_attribute_coverage_pct": average_coverage
        })

    return summary


def save_csv(filename, records):

    if not records:
        print("No records to save:", filename)
        return

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=records[0].keys()
        )

        writer.writeheader()
        writer.writerows(records)


def save_methodology():

    methodology = """
TAMIL NADU FOOTPATH ACCESSIBILITY ANALYZER

SCORING METHODOLOGY
===================

Data source:
OpenStreetMap (OSM)

Model:
Weighted OSM evidence scoring model.

ATTRIBUTE WEIGHTS
-----------------
Wheelchair accessibility: 30
Width: 20
Surface: 15
Kerb: 15
Tactile paving: 10
Sidewalk: 10

TOTAL WEIGHT: 100

SCORING
-------
Positive mapped evidence: 100
Partially supportive evidence: 60 or 70
Negative mapped evidence: 0
Missing or unrecognized information: Unknown

The evidence score is calculated using only
attributes with recognized mapped values.

Attribute coverage measures the percentage
of total attribute weight represented by
recognized OSM information.

EVIDENCE COVERAGE LEVELS
------------------------
Below 30%: Insufficient evidence
30% to below 50%: Limited evidence
50% to below 75%: Moderate evidence
75% and above: Strong evidence coverage

IMPORTANT LIMITATIONS
---------------------
1. OSM tags are not field-verified measurements.
2. Missing values are not treated as negative.
3. The evidence score is not a certified
   accessibility rating.
4. Results should not be interpreted as proof
   of actual pedestrian accessibility.
5. Width thresholds are preliminary analytical
   assumptions, not a compliance certification.

Generated on: DATE_PLACEHOLDER
"""

    methodology = methodology.replace(
        "DATE_PLACEHOLDER",
        date.today().isoformat()
    )

    with open(
        METHOD_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(methodology)


def main():

    print("=" * 55)
    print("TAMIL NADU ACCESSIBILITY SCORING ENGINE")
    print("=" * 55)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    records = load_records()

    scored_records = []

    print("\nCalculating accessibility evidence scores...")

    for index, record in enumerate(records, start=1):

        score_data = calculate_score(record)

        scored_record = {
            **record,
            **score_data
        }

        scored_records.append(scored_record)

        if index % 1000 == 0:
            print("Processed:", index)

    save_csv(SCORED_FILE, scored_records)

    district_summary = generate_district_summary(
        scored_records
    )

    save_csv(DISTRICT_FILE, district_summary)

    save_methodology()

    scored_count = sum(
        r["accessibility_evidence_score"] != ""
        for r in scored_records
    )

    print("\n" + "=" * 55)
    print("SCORING SUMMARY")
    print("=" * 55)

    print("Total records:", len(scored_records))
    print("Districts:", len(district_summary))
    print("Records scored:", scored_count)
    print("Records without sufficient mapped attributes:",
          len(scored_records) - scored_count)

    print("\nOUTPUT FILES")
    print("Scored dataset:", SCORED_FILE)
    print("District summary:", DISTRICT_FILE)
    print("Methodology:", METHOD_FILE)

    print("\nACCESSIBILITY SCORING COMPLETED")


if __name__ == "__main__":
    main()
