
import csv
from pathlib import Path

import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "district_accessibility_summary.csv"
)

OUTPUT_DIR = (
    BASE_DIR / "data" / "processed"
    / "district_comparison"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_data():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Scoring summary not found: {INPUT_FILE}\n"
            "Run accessibility_scoring.py first."
        )

    with open(INPUT_FILE, encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def prepare_data(records):

    prepared = []

    for row in records:

        score = row.get("average_evidence_score", "")
        coverage = row.get(
            "average_attribute_coverage_pct", ""
        )

        try:
            score = float(score) if score else None
            coverage = float(coverage) if coverage else 0
        except ValueError:
            score = None
            coverage = 0

        prepared.append({
            "district": row["district"],
            "total_records": int(row["total_records"]),
            "records_with_score": int(row["records_with_score"]),
            "average_evidence_score": score,
            "average_attribute_coverage_pct": coverage
        })

    return prepared


def save_comparison(records):

    output_file = OUTPUT_DIR / "district_comparison.csv"

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        fields = [
            "district",
            "total_records",
            "records_with_score",
            "average_evidence_score",
            "average_attribute_coverage_pct"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        writer.writeheader()
        writer.writerows(records)

    return output_file


def create_score_chart(records):

    valid = [
        row for row in records
        if row["average_evidence_score"] is not None
    ]

    valid.sort(
        key=lambda x: x["average_evidence_score"],
        reverse=True
    )

    districts = [r["district"] for r in valid]
    scores = [
        r["average_evidence_score"] for r in valid
    ]

    plt.figure(figsize=(16, 9))

    plt.bar(districts, scores)

    plt.title(
        "District-wise Accessibility Evidence Scores"
    )
    plt.xlabel("Tamil Nadu Districts")
    plt.ylabel("Average Evidence Score")

    plt.xticks(rotation=90)
    plt.ylim(0, 100)

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "district_evidence_scores.png",
        dpi=300
    )

    plt.close()


def create_top_bottom_chart(records):

    valid = [
        row for row in records
        if row["average_evidence_score"] is not None
    ]

    valid.sort(
        key=lambda x: x["average_evidence_score"],
        reverse=True
    )

    top = valid[:10]
    bottom = valid[-10:]

    fig, axes = plt.subplots(
        1, 2,
        figsize=(16, 7)
    )

    axes[0].bar(
        [r["district"] for r in top],
        [r["average_evidence_score"] for r in top]
    )

    axes[0].set_title("Top 10 Districts")
    axes[0].set_ylabel("Average Evidence Score")
    axes[0].tick_params(axis="x", rotation=45)
    axes[0].set_ylim(0, 100)

    axes[1].bar(
        [r["district"] for r in bottom],
        [r["average_evidence_score"] for r in bottom]
    )

    axes[1].set_title("Bottom 10 Districts")
    axes[1].set_ylabel("Average Evidence Score")
    axes[1].tick_params(axis="x", rotation=45)
    axes[1].set_ylim(0, 100)

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "top_bottom_districts.png",
        dpi=300
    )

    plt.close()


def create_coverage_chart(records):

    ordered = sorted(
        records,
        key=lambda x: x["average_attribute_coverage_pct"],
        reverse=True
    )

    districts = [r["district"] for r in ordered]
    coverage = [
        r["average_attribute_coverage_pct"]
        for r in ordered
    ]

    plt.figure(figsize=(16, 9))

    plt.bar(districts, coverage)

    plt.title(
        "District-wise Accessibility Attribute Coverage"
    )

    plt.xlabel("District")
    plt.ylabel("Attribute Coverage (%)")

    plt.xticks(rotation=90)
    plt.ylim(0, 100)

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "district_attribute_coverage.png",
        dpi=300
    )

    plt.close()


def main():

    print("=" * 55)
    print("DISTRICT ACCESSIBILITY COMPARISON")
    print("=" * 55)

    records = load_data()
    prepared = prepare_data(records)

    valid = [
        r for r in prepared
        if r["average_evidence_score"] is not None
    ]

    if not valid:
        print("No valid district scores available.")
        return

    ordered = sorted(
        prepared,
        key=lambda x: (
            x["average_evidence_score"] is None,
            -(x["average_evidence_score"] or 0)
        )
    )

    save_comparison(ordered)

    create_score_chart(prepared)
    create_top_bottom_chart(prepared)
    create_coverage_chart(prepared)

    print("\nCOMPARISON SUMMARY")
    print("Districts found:", len(prepared))
    print("Districts with scores:", len(valid))
    print("Districts without scores:", len(prepared) - len(valid))

    print("\nTOP 10 DISTRICTS")

    for index, row in enumerate(valid[:10], start=1):
        ranked = sorted(
            valid,
            key=lambda x: x["average_evidence_score"],
            reverse=True
        )
        item = ranked[index - 1]

        print(
            index,
            item["district"],
            item["average_evidence_score"]
        )

    print("\nOUTPUT DIRECTORY:")
    print(OUTPUT_DIR)

    print("\nDISTRICT COMPARISON COMPLETED")


if __name__ == "__main__":
    main()
