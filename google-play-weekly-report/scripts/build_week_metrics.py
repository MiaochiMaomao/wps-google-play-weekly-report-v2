from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def percentage(count: int, total: int, decimals: int) -> float:
    return round(count * 100 / total, decimals) if total else 0.0


def apply_sort(rows: list[dict], specifications: list[str]) -> None:
    for specification in reversed(specifications):
        descending = specification.startswith("-")
        key = specification.lstrip("+-")
        rows.sort(key=lambda row: row[key], reverse=descending)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    audit = json.loads(Path(args.audit).read_text(encoding="utf-8"))
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    if audit.get("needs_user"):
        raise SystemExit("Input audit requires user confirmation; metrics were not built.")

    decimals = config["format"]["percentage_decimals"]
    low_ratings = set(config["metrics"]["low_ratings"])
    high_ratings = set(config["metrics"]["high_ratings"])
    categories = config["classification"]["categories"]
    representative = config["classification"]["representative_category"]
    all_rows = audit["all_reviews"]["rows"]
    detail = audit["classified_reviews"]["rows"]

    rating_stars = Counter(row["rating"] for row in all_rows)
    comment_rows = [row for row in all_rows if row["review"]]
    comment_stars = Counter(row["rating"] for row in comment_rows)
    category_counts = Counter(row["category"] for row in detail)
    subcategory_counts = {
        category: Counter(row["subcategory"] for row in detail if row["category"] == category)
        for category in categories
    }

    version_source = comment_rows if config["metrics"]["version_scope"] == "comments" else all_rows
    versions = defaultdict(Counter)
    for row in version_source:
        version = row["version"]
        if not version:
            continue
        versions[version]["total"] += 1
        versions[version][f"star_{row['rating']}"] += 1
    version_rows = []
    for version, counts in versions.items():
        if counts["total"] < config["metrics"]["version_min_comments"]:
            continue
        low = sum(counts[f"star_{rating}"] for rating in low_ratings)
        high = sum(counts[f"star_{rating}"] for rating in high_ratings)
        version_rows.append({
            "version": version,
            "total": counts["total"],
            "low": low,
            "low_rate": percentage(low, counts["total"], decimals),
            "high": high,
            "high_rate": percentage(high, counts["total"], decimals),
        })
    apply_sort(version_rows, config["metrics"]["version_sort"])

    representative_counts = subcategory_counts[representative]
    candidate_rows = defaultdict(list)
    minimum = config["metrics"]["representative_comment_min_chars"]
    maximum = config["metrics"]["representative_comment_max_chars"]
    for row in detail:
        if row["category"] != representative:
            continue
        if minimum <= len(row["original"]) <= maximum:
            candidate_rows[row["subcategory"]].append({
                "original": row["original"],
                "translation": row["translation"],
                "date": row["date"],
                "rating": row["rating"],
            })
    ordered = sorted(representative_counts.items(), key=lambda item: (-item[1], item[0]))
    top_issues = []
    for name, count in ordered[: config["metrics"]["issue_top_n"]]:
        candidates = sorted(candidate_rows[name], key=lambda row: (len(row["original"]), row["original"]))
        top_issues.append({
            "name": name,
            "count": count,
            "share": percentage(count, sum(representative_counts.values()), decimals),
            "candidates": candidates,
        })

    low_rating_total = sum(rating_stars[rating] for rating in low_ratings)
    high_rating_total = sum(rating_stars[rating] for rating in high_ratings)
    low_comment_total = sum(comment_stars[rating] for rating in low_ratings)
    high_comment_total = sum(comment_stars[rating] for rating in high_ratings)

    result = {
        "period": audit["period"],
        "global": {
            "rating_total": len(all_rows),
            "rating_stars": {str(value): rating_stars[value] for value in range(1, 6)},
            "rating_low": low_rating_total,
            "rating_low_rate": percentage(low_rating_total, len(all_rows), decimals),
            "rating_high": high_rating_total,
            "rating_high_rate": percentage(high_rating_total, len(all_rows), decimals),
            "comment_total": len(comment_rows),
            "comment_stars": {str(value): comment_stars[value] for value in range(1, 6)},
            "comment_low": low_comment_total,
            "comment_low_rate": percentage(low_comment_total, len(comment_rows), decimals),
            "comment_high": high_comment_total,
            "comment_high_rate": percentage(high_comment_total, len(comment_rows), decimals),
        },
        "major_categories": [
            {"name": name, "count": category_counts[name], "share": percentage(category_counts[name], len(detail), decimals)}
            for name in categories
        ],
        "subcategory_categories": {
            category: [
                {"name": name, "count": count, "share": percentage(count, sum(subcategory_counts[category].values()), decimals)}
                for name, count in subcategory_counts[category].most_common()
            ]
            for category in categories
        },
        "representative_category": representative,
        "representative_subcategories": [
            {"name": name, "count": count, "share": percentage(count, sum(representative_counts.values()), decimals)}
            for name, count in representative_counts.most_common()
        ],
        "versions": version_rows[: config["metrics"]["version_top_n"]],
        "top_issues": top_issues,
        "source": {
            "workbook": audit["workbook"],
            "all_reviews_sheet": audit["all_reviews"]["sheet"],
            "classified_reviews_sheet": audit["classified_reviews"]["sheet"],
        },
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "period": result["period"],
        "rating_total": result["global"]["rating_total"],
        "comment_total": result["global"]["comment_total"],
        "categories": {row["name"]: row["count"] for row in result["major_categories"]},
        "versions": [row["version"] for row in result["versions"]],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

