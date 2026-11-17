
import json
import csv
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = (
    BASE_DIR / "data" / "raw" / "districts" / "full_collection"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed"

OUTPUT_FILE = OUTPUT_DIR / "tn_footpath_accessibility.csv"
REPORT_FILE = OUTPUT_DIR / "processing_report.csv"


FIELDS = [
    "source",
    "source_url",
    "source_record_id",
    "retrieved_on",
    "district",
    "osm_type",
    "osm_id",
    "feature_type",
    "latitude",
    "longitude",
    "highway",
    "footway",
    "sidewalk",
    "surface",
    "width",
    "wheelchair",
    "tactile_paving",
    "kerb",
    "evidence_status"
]


def classify_feature(tags):

    highway = tags.get("highway", "")
    footway = tags.get("footway", "")
    sidewalk = tags.get("sidewalk", "")

    if highway == "crossing" or footway == "crossing":
        return "crossing"

    if highway == "footway":
        if footway == "sidewalk":
            return "sidewalk"

        return "footway"

    if footway == "sidewalk":
        return "sidewalk"

    if sidewalk in ["yes", "both", "left", "right"]:
        return "sidewalk"

    return None


def get_coordinates(element):

    # Overpass way elements generally provide a center.
    center = element.get("center")

    if center:
        return center.get("lat"), center.get("lon")

    # Overpass node elements provide direct coordinates.
    lat = element.get("lat")
    lon = element.get("lon")

    if lat is not None and lon is not None:
        return lat, lon

    return None, None


def process_district(file_path):

    district = (
        file_path.stem
        .replace("_osm_full", "")
        .replace("_", " ")
        .title()
    )

    print(f"\nProcessing: {district}")

    with open(file_path, encoding="utf-8") as file:
        data = json.load(file)

    elements = data.get("elements", [])

    records = []
    seen_ids = set()

    for element in elements:

        tags = element.get("tags") or {}

        feature_type = classify_feature(tags)

        if feature_type is None:
            continue

        osm_type = element.get("type")
        osm_id = element.get("id")

        if osm_type is None or osm_id is None:
            continue

        record_id = f"{osm_type}/{osm_id}"

        if record_id in seen_ids:
            continue

        lat, lon = get_coordinates(element)

        if lat is None or lon is None:
            continue

        seen_ids.add(record_id)

        records.append({
            "source": "OpenStreetMap",
            "source_url": (
                f"https://www.openstreetmap.org/"
                f"{osm_type}/{osm_id}"
            ),
            "source_record_id": record_id,
            "retrieved_on": date.today().isoformat(),
            "district": district,
            "osm_type": osm_type,
            "osm_id": osm_id,
            "feature_type": feature_type,
            "latitude": lat,
            "longitude": lon,
            "highway": tags.get("highway"),
            "footway": tags.get("footway"),
            "sidewalk": tags.get("sidewalk"),
            "surface": tags.get("surface"),
            "width": tags.get("width"),
            "wheelchair": tags.get("wheelchair"),
            "tactile_paving": tags.get("tactile_paving"),
            "kerb": tags.get("kerb"),
            "evidence_status": "source_mapped"
        })

    return records, len(elements)


def main():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(INPUT_DIR.glob("*_osm_full.json"))

    if not files:
        print("ERROR: No district JSON files found.")
        return

    all_records = []
    report = []

    print("=" * 55)
    print("TAMIL NADU FOOTPATH DATA PROCESSOR")
    print("=" * 55)

    for file_path in files:

        try:

            records, input_count = process_district(file_path)

            all_records.extend(records)

            report.append({
                "district": file_path.stem.replace(
                    "_osm_full", ""
                ).replace("_", " ").title(),
                "status": "success",
                "input_elements": input_count,
                "extracted_records": len(records)
            })

            print("Extracted records:", len(records))

        except Exception as error:

            print("FAILED:", file_path.name, error)

            report.append({
                "district": file_path.stem,
                "status": "failed",
                "input_elements": 0,
                "extracted_records": 0
            })

    # Save consolidated dataset.
    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDS
        )

        writer.writeheader()
        writer.writerows(all_records)

    # Save processing report.
    with open(
        REPORT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "district",
                "status",
                "input_elements",
                "extracted_records"
            ]
        )

        writer.writeheader()
        writer.writerows(report)

    successful = sum(
        item["status"] == "success"
        for item in report
    )

    failed = sum(
        item["status"] == "failed"
        for item in report
    )

    print("\n" + "=" * 55)
    print("PROCESSING SUMMARY")
    print("=" * 55)

    print("District files found:", len(files))
    print("Successful districts:", successful)
    print("Failed districts:", failed)
    print("Total extracted records:", len(all_records))

    print("\nDataset saved:", OUTPUT_FILE)
    print("Report saved:", REPORT_FILE)

    print("\nPROCESSING COMPLETED")


if __name__ == "__main__":
    main()
