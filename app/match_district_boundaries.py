
import json
import re
import csv
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "raw" / "tn_district_boundaries.geojson"
REPORT_FILE = BASE_DIR / "data" / "processed" / "boundary_match_report.csv"

EXPECTED_DISTRICTS = [
    "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore",
    "Cuddalore", "Dharmapuri", "Dindigul", "Erode",
    "Kallakurichi", "Kancheepuram", "Kanniyakumari",
    "Karur", "Krishnagiri", "Madurai", "Mayiladuthurai",
    "Nagapattinam", "Namakkal", "Perambalur", "Pudukkottai",
    "Ramanathapuram", "Ranipet", "Salem", "Sivaganga",
    "Tenkasi", "Thanjavur", "Theni", "Thoothukudi",
    "Tiruchirappalli", "Tirunelveli", "Tirupathur",
    "Tiruppur", "Tiruvallur", "Tiruvannamalai",
    "Tiruvarur", "The Nilgiris", "Vellore",
    "Viluppuram", "Virudhunagar"
]


ALIASES = {
    "nilgiris": "the nilgiris",
    "kanchipuram": "kancheepuram",
    "kanyakumari": "kanniyakumari",
    "tirupattur": "tirupathur",
    "sivagangai": "sivaganga",
    "thiruvallur": "tiruvallur",
    "thiruvarur": "tiruvarur"
}




def normalize(name):
    name = name.strip().lower()
    name = re.sub(r"\s+", " ", name)

    # Remove administrative suffix
    name = re.sub(r"\s+district$", "", name)

    return ALIASES.get(name, name)



def main():

    with open(INPUT_FILE, encoding="utf-8") as file:
        data = json.load(file)

    features = data.get("features", [])

    expected = {
        normalize(name): name
        for name in EXPECTED_DISTRICTS
    }

    found = {}
    rows = []
    invalid_admin = []
    missing_ids = []

    for feature in features:

        props = feature.get("properties") or {}

        name = props.get("name:en") or props.get("name") or ""
        osm_id = props.get("@id") or feature.get("id")
        admin_level = str(props.get("admin_level", ""))

        key = normalize(name)

        if not osm_id:
            missing_ids.append(name)

        if admin_level != "5":
            invalid_admin.append(name)

        matched = key in expected

        rows.append({
            "osm_name": name,
            "matched_district": expected.get(key, ""),
            "osm_relation_id": osm_id,
            "admin_level": admin_level,
            "match_status": "matched" if matched else "unmatched"
        })

        if matched:
            found.setdefault(key, []).append(osm_id)

            print("\n===== UNMATCHED OSM DISTRICTS =====")

            for row in rows:
                if row["match_status"] == "unmatched":
                 print(
                    "OSM Name:", repr(row["osm_name"]),
                        "| Relation ID:", row["osm_relation_id"]
                )

    missing = [
        name for key, name in expected.items()
        if key not in found
    ]

    duplicates = {
        expected[key]: ids
        for key, ids in found.items()
        if len(ids) > 1
    }

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(REPORT_FILE, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print("\n===== DISTRICT BOUNDARY MATCH REPORT =====")
    print("Expected districts:", len(expected))
    print("Boundary features:", len(features))
    print("Matched districts:", len(found))
    print("Missing districts:", missing)
    print("Duplicate district matches:", duplicates)
    print("Missing relation IDs:", missing_ids)
    print("Invalid admin levels:", invalid_admin)

    if len(found) == 38 and not missing and not duplicates \
            and not missing_ids and not invalid_admin:
        print("\nBOUNDARY MATCH CHECK PASSED")
    else:
        print("\nBOUNDARY MATCH NEEDS REVIEW")

    print("Report saved:", REPORT_FILE)


if __name__ == "__main__":
    main()
