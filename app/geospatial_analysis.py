
import csv
from pathlib import Path
from collections import Counter

import folium
from folium.plugins import MarkerCluster

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "tn_accessibility_scored.csv"
)

OUTPUT_DIR = (
    BASE_DIR / "data" / "processed"
    / "geospatial_maps"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Approximate centre of Tamil Nadu
TN_CENTER = [10.7905, 78.7047]


def load_data():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Scored dataset not found: {INPUT_FILE}. "
            "Run accessibility_scoring.py first."
        )

    with open(INPUT_FILE, encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def create_map(records):

    map_object = folium.Map(
        location=TN_CENTER,
        zoom_start=7,
        tiles="OpenStreetMap"
    )

    clusters = {
        "footway": MarkerCluster(name="Footways"),
        "sidewalk": MarkerCluster(name="Sidewalks"),
        "crossing": MarkerCluster(name="Crossings")
    }

    colors = {
        "footway": "blue",
        "sidewalk": "green",
        "crossing": "orange"
    }

    counts = Counter()

    # Plot mapped OSM features
    for record in records:

        try:
            lat = float(record["latitude"])
            lon = float(record["longitude"])

            feature = record["feature_type"]

            if feature not in clusters:
                continue

            if not (8 <= lat <= 14 and 76 <= lon <= 81):
                continue

            source_id = record["source_record_id"]

            score = record.get(
                "accessibility_evidence_score", ""
            )

            popup_text = f"""
            <b>District:</b> {record['district']}<br>
            <b>Feature:</b> {feature}<br>
            <b>OSM ID:</b> {source_id}<br>
            <b>Evidence score:</b> {score or 'Unknown'}<br>
            <b>Wheelchair:</b> {record.get('wheelchair', '') or 'Unknown'}<br>
            <b>Surface:</b> {record.get('surface', '') or 'Unknown'}
            """

            folium.CircleMarker(
                location=[lat, lon],
                radius=3,
                color=colors[feature],
                fill=True,
                fill_opacity=0.7,
                popup=folium.Popup(
                    popup_text,
                    max_width=300
                )
            ).add_to(clusters[feature])

            counts[feature] += 1

        except (ValueError, KeyError, TypeError):
            continue

    for cluster in clusters.values():
        cluster.add_to(map_object)

    folium.LayerControl().add_to(map_object)

    map_object.save(
        OUTPUT_DIR / "tamil_nadu_footpath_map.html"
    )

    return counts


def create_district_maps(records):

    districts = sorted({
        record["district"]
        for record in records
        if record.get("district")
    })

    for district in districts:

        district_map = folium.Map(
            location=TN_CENTER,
            zoom_start=9,
            tiles="OpenStreetMap"
        )

        count = 0

        for record in records:

            if record["district"] != district:
                continue

            try:
                lat = float(record["latitude"])
                lon = float(record["longitude"])

                if not (8 <= lat <= 14 and 76 <= lon <= 81):
                    continue

                folium.CircleMarker(
                    location=[lat, lon],
                    radius=3,
                    color="blue",
                    fill=True,
                    popup=(
                        f"{district} | "
                        f"{record['feature_type']} | "
                        f"{record['source_record_id']}"
                    )
                ).add_to(district_map)

                count += 1

            except (ValueError, KeyError, TypeError):
                continue

        filename = (
            district.lower().replace(" ", "_")
            + "_map.html"
        )

        district_map.save(OUTPUT_DIR / filename)

        print(district, ":", count, "mapped features")


def main():

    print("=" * 55)
    print("TAMIL NADU GEOSPATIAL ANALYSIS")
    print("=" * 55)

    records = load_data()

    print("Input records:", len(records))

    counts = create_map(records)

    print("\nFEATURE COUNTS")

    for feature, count in counts.items():
        print(feature, ":", count)

    print("\nGENERATING DISTRICT MAPS")

    create_district_maps(records)

    print("\nOUTPUT DIRECTORY:")
    print(OUTPUT_DIR)

    print("\nGEOSPATIAL ANALYSIS COMPLETED")


if __name__ == "__main__":
    main()
