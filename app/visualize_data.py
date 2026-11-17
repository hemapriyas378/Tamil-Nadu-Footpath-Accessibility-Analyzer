
import csv
from pathlib import Path
from collections import Counter

import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "tn_footpath_accessibility_cleaned.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed" / "visualizations"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_data():
    with open(INPUT_FILE, encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def visualize():

    records = load_data()

    if not records:
        print("No records found!")
        return

    district_counts = Counter(
        row["district"] for row in records
    )

    feature_counts = Counter(
        row["feature_type"] for row in records
    )

    # 1. District-wise distribution
    districts = sorted(district_counts)
    counts = [district_counts[d] for d in districts]

    plt.figure(figsize=(15, 8))
    plt.bar(districts, counts)
    plt.xticks(rotation=90)
    plt.title("OSM Mapped Features by District")
    plt.xlabel("District")
    plt.ylabel("Number of Records")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "district_distribution.png")
    plt.close()

    # 2. Feature distribution
    plt.figure(figsize=(8, 6))
    plt.bar(feature_counts.keys(), feature_counts.values())
    plt.title("Feature Type Distribution")
    plt.xlabel("Feature Type")
    plt.ylabel("Number of Records")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "feature_distribution.png")
    plt.close()

    # 3. Top 10 districts
    top_districts = district_counts.most_common(10)

    plt.figure(figsize=(10, 6))
    plt.bar(
        [x[0] for x in top_districts],
        [x[1] for x in top_districts]
    )
    plt.xticks(rotation=45)
    plt.title("Top 10 Districts by Mapped Features")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "top_10_districts.png")
    plt.close()

    # 4. Attribute coverage
    attributes = [
        "width",
        "surface",
        "wheelchair",
        "tactile_paving",
        "kerb"
    ]

    coverage = {
        field: sum(
            bool(row.get(field, "").strip())
            for row in records
        )
        for field in attributes
    }

    plt.figure(figsize=(10, 6))
    plt.bar(coverage.keys(), coverage.values())
    plt.title("Accessibility Attribute Availability")
    plt.ylabel("Records with mapped attribute")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "attribute_coverage.png")
    plt.close()

    print("\nVISUALIZATION COMPLETED")
    print("Total records:", len(records))
    print("Districts:", len(district_counts))
    print("Output directory:", OUTPUT_DIR)


if __name__ == "__main__":
    visualize()
