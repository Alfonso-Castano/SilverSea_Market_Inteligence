# pipeline/report.py — Writes the structured report JSON to data/latest_report.json
import json
import os
import datetime

REPORT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "latest_report.json")


def save_report_json(report_data: dict, country_name: str) -> None:
    """Save structured report data as JSON for the Flask dashboard to render."""
    report_data["_metadata"] = {
        "country": country_name,
        "date": datetime.date.today().isoformat(),
        "date_display": datetime.date.today().strftime("%d %B %Y"),
    }

    os.makedirs(os.path.dirname(os.path.abspath(REPORT_PATH)), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"  Report JSON written to {os.path.abspath(REPORT_PATH)}")
