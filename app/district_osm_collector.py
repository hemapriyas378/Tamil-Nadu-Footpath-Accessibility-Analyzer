
import csv
import json
import re
import time
import urllib.request
import urllib.parse
import urllib.error

from pathlib import Path
from datetime import datetime, timezone


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

BOUNDARY_FILE = (
    BASE_DIR / "data" / "processed" /
    "boundary_match_report.csv"
)

OUTPUT_DIR = (
    BASE_DIR / "data" / "raw" /
    "districts" / "full_collection"
)

REPORT_DIR = BASE_DIR / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# OVERPASS CONFIGURATION
# --------------------------------------------------

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

USER_AGENT = "TN-Footpath-Accessibility-Analyzer/0.1"

REQUEST_TIMEOUT = 240
MAX_RETRIES = 3
DELAY_BETWEEN_DISTRICTS = 30


TARGET_DISTRICTS = [
    "Perambalur",
    "Tenkasi"
]


# --------------------------------------------------
# LOAD VERIFIED DISTRICT RELATION IDS
# --------------------------------------------------

def load_districts():

    if not BOUNDARY_FILE.exists():
        raise FileNotFoundError(
            f"Boundary report not found: {BOUNDARY_FILE}"
        )

    districts = []

    with open(
        BOUNDARY_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        required_columns = {
            "matched_district",
            "osm_relation_id",
            "admin_level",
            "match_status"
        }

        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError(
                "Boundary report has unexpected columns."
            )

        for row in reader:

            if row["match_status"].strip() != "matched":
                continue

            if row["admin_level"].strip() != "5":
                raise ValueError(
                    f"Invalid admin level: {row}"
                )

            raw_id = row["osm_relation_id"].strip()

            match = re.fullmatch(r"relation/(\d+)", raw_id)

            if not match:
                raise ValueError(
                    f"Invalid relation ID: {raw_id}"
                )

            districts.append({
                "district": row["matched_district"].strip(),
                "relation_id": int(match.group(1))
            })

    names = [d["district"].casefold() for d in districts]
    relation_ids = [d["relation_id"] for d in districts]

    if len(districts) != 38:
        raise ValueError(
            f"Expected 38 matched districts, found {len(districts)}"
        )

    if len(set(names)) != 38:
        raise ValueError("Duplicate district names detected.")

    if len(set(relation_ids)) != 38:
        raise ValueError("Duplicate relation IDs detected.")

    print("Verified district boundaries loaded:", len(districts))

    return districts


# --------------------------------------------------
# BUILD OVERPASS QUERY USING RELATION ID
# --------------------------------------------------

def create_query(relation_id):

    return f"""
    [out:json][timeout:180];

    rel({relation_id});
    map_to_area->.district;

    (
      way["highway"="footway"](area.district);
      way["footway"~"sidewalk|crossing"](area.district);
      way["sidewalk"~"yes|both|left|right"](area.district);
      node["highway"="crossing"](area.district);
    );

    out center tags;
    """


# --------------------------------------------------
# FETCH DISTRICT DATA
# --------------------------------------------------

def fetch_district_data(district, relation_id):

    query = create_query(relation_id)

    request_data = urllib.parse.urlencode({
        "data": query
    }).encode("utf-8")

    for attempt in range(MAX_RETRIES):

        request = urllib.request.Request(
            OVERPASS_URL,
            data=request_data,
            headers={
                "User-Agent": USER_AGENT,
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )

        try:

            print(f"\nFetching district: {district}")
            print(f"Verified relation ID: {relation_id}")

            with urllib.request.urlopen(
                request,
                timeout=REQUEST_TIMEOUT
            ) as response:

                data = json.loads(
                    response.read().decode("utf-8")
                )

            if "elements" not in data:
                raise ValueError(
                    "Overpass response does not contain elements."
                )

            return data

        except urllib.error.HTTPError as error:

            print("HTTP error:", error.code)

            if error.code not in (429, 502, 503, 504):
                raise

            retry_after = error.headers.get("Retry-After")

            try:
                wait = int(retry_after)
            except (TypeError, ValueError):
                wait = 60 * (attempt + 1)

        except Exception as error:

            print("Request failed:", error)
            wait = 30 * (attempt + 1)

        if attempt < MAX_RETRIES - 1:

            print(f"Retrying after {wait} seconds...")
            time.sleep(wait)

    return None


# --------------------------------------------------
# SAVE RAW DISTRICT JSON
# --------------------------------------------------

def save_district_data(district, relation_id, data):

    filename = (
        district.lower().replace(" ", "_")
        + "_osm_full.json"
    )

    output_file = OUTPUT_DIR / filename

    # Preserve the original Overpass response.
    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )

    return output_file


# --------------------------------------------------
# MAIN COLLECTION PROCESS
# --------------------------------------------------

def main():

    print("=" * 55)
    print("TAMIL NADU FOOTPATH ACCESSIBILITY ANALYZER")
    print("38-DISTRICT OSM COLLECTION")
    print("=" * 55)

    districts = load_districts()

    if TARGET_DISTRICTS is not None:

        target_names = {
            name.casefold() for name in TARGET_DISTRICTS
        }

        districts = [
            d for d in districts
            if d["district"].casefold() in target_names
        ]

        if len(districts) != len(target_names):
            raise ValueError(
                "One or more requested districts were not found."
            )

    print("Districts selected:", len(districts))

    report = []

    for index, item in enumerate(districts):

        district = item["district"]
        relation_id = item["relation_id"]

        try:

            data = fetch_district_data(
                district,
                relation_id
            )

            if data is None:

                report.append({
                    "district": district,
                    "relation_id": relation_id,
                    "status": "failed",
                    "records": 0,
                    "file": ""
                })

            else:

                elements = data.get("elements", [])

                output_file = save_district_data(
                    district,
                    relation_id,
                    data
                )

                report.append({
                    "district": district,
                    "relation_id": relation_id,
                    "status": "success",
                    "records": len(elements),
                    "file": str(output_file)
                })

                print("Records:", len(elements))
                print("Saved:", output_file)

        except Exception as error:

            print("District processing error:", error)

            report.append({
                "district": district,
                "relation_id": relation_id,
                "status": "failed",
                "records": 0,
                "file": ""
            })

        if index < len(districts) - 1:
            print(
                f"Waiting {DELAY_BETWEEN_DISTRICTS} seconds..."
            )
            time.sleep(DELAY_BETWEEN_DISTRICTS)

    # --------------------------------------------------
    # SAVE COLLECTION REPORT
    # --------------------------------------------------

    report_file = (
        REPORT_DIR / "district_collection_report.csv"
    )

    with open(
        report_file,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        fieldnames = [
            "district",
            "relation_id",
            "status",
            "records",
            "file"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(report)

    successful = sum(
        row["status"] == "success"
        for row in report
    )

    total_records = sum(
        row["records"]
        for row in report
    )

    print("\n" + "=" * 55)
    print("COLLECTION SUMMARY")
    print("=" * 55)

    print("Districts selected:", len(districts))
    print("Successful districts:", successful)
    print("Failed districts:", len(districts) - successful)
    print("Total raw OSM elements:", total_records)
    print("Collection report:", report_file)
    print("Collection finished.")


if __name__ == "__main__":
    main()
