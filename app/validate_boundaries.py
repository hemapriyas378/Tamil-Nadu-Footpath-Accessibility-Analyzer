
import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "raw" / "tn_district_boundaries.geojson"

def validate_boundaries():

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    features = data.get("features", [])

    names = []

    for feature in features:
        properties = feature.get("properties", {})

        name = (
            properties.get("name:en")
            or properties.get("name")
            or properties.get("official_name")
        )

        if name:
            names.append(name)

        print(
            "District:", name,
            "| OSM ID:", properties.get("@id"),
            "| Admin Level:", properties.get("admin_level")
        )

    duplicates = [
        name for name, count in Counter(names).items()
        if count > 1
    ]

    print("\n========== BOUNDARY REPORT ==========")
    print("Total boundary features:", len(features))
    print("District names found:", len(names))
    print("Duplicate names:", duplicates)

    print("\nBOUNDARY VALIDATION FINISHED")


if __name__ == "__main__":
    validate_boundaries()
