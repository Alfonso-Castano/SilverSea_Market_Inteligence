# pipeline/report.py — Writes the structured report JSON to data/latest_report.json
import json
import os
import datetime

REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
REPORT_PATH = os.path.join(REPORT_DIR, "latest_report.json")


def save_report_json(report_data: dict, country_name: str, country_code: str = None, domain: str = None) -> None:
    """Save structured report data as JSON for the Flask dashboard to render.

    When `domain` is specified (and `country_code` is available), the report is written to a
    domain-scoped filename (`latest_report_{country_code}_{domain}.json`) instead of the default
    `latest_report.json`, so a --domain=BER run doesn't clobber a --domain=EDU run's output.
    When `domain` is None (the default), behavior is unchanged from before domain-scoping existed.
    """
    report_data["_metadata"] = {
        "country": country_name,
        "date": datetime.date.today().isoformat(),
        "date_display": datetime.date.today().strftime("%d %B %Y"),
    }

    if domain and country_code:
        report_path = os.path.join(REPORT_DIR, f"latest_report_{country_code}_{domain}.json")
    else:
        report_path = REPORT_PATH

    os.makedirs(os.path.dirname(os.path.abspath(report_path)), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)

    print(f"  Report JSON written to {os.path.abspath(report_path)}")
