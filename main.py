# main.py — Runs the full market intelligence pipeline end-to-end
import json
import os
import sys
import datetime
from dotenv import load_dotenv
load_dotenv()
from config.sources import COUNTRIES
from pipeline.scraper import scrape_all
from pipeline.filter import filter_results
from pipeline.dedup import deduplicate
from pipeline.entities import extract_entities
from pipeline.analyst import analyse
from pipeline.report import save_report_json
from pipeline.emailer import send_digest
from pipeline.scoring import update_scores
from pipeline.feedback import aggregate_feedback


def _format_email_text(report_data: dict) -> str:
    """Format structured report dict into plain text for email digest."""
    lines = []
    lines.append("EXECUTIVE SUMMARY")
    for bullet in report_data.get("executive_summary", []):
        lines.append(f"- {bullet}")
    lines.append("")

    for opp in report_data.get("opportunities", []):
        lines.append(f"OPPORTUNITY: {opp.get('title', 'Untitled')} (Score: {opp.get('total_score', '?')}/25)")
        lines.append(f"  Action: {opp.get('concrete_action', '')}")
        lines.append(f"  Product fit: {opp.get('product_fit', '')}")
        lines.append("")

    for bullet in report_data.get("synthesis", []):
        lines.append(f"- {bullet}")

    return "\n".join(lines)


def run_pipeline(send_email: bool = True) -> None:
    active_countries = [c for c in COUNTRIES if c["active"]]
    print(f"Running pipeline for {len(active_countries)} active country/countries...\n")

    print("Processing feedback from previous run...")
    aggregate_feedback()

    for country in active_countries:
        print(f"=== {country['name']} ({country['code']}) ===")

        print("Scraping sources...")
        scraped = scrape_all(country["sources"])

        print("Filtering content...")
        filtered = filter_results(scraped, country["keywords"])

        if not filtered:
            print("  No relevant content found — skipping LLM analysis.\n")
            continue

        print("Deduplicating signals...")
        deduped = deduplicate(filtered)

        print("Extracting entities...")
        enriched = extract_entities(deduped)

        print("Analysing with Claude...")
        report_data = analyse(enriched, country)

        print("Scoring sources...")
        report_text_for_scoring = json.dumps(report_data, ensure_ascii=False)
        update_scores(filtered, report_text_for_scoring)

        print("Saving report JSON...")
        save_report_json(report_data, country["name"])

        run_metadata = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "country": country["name"],
            "country_code": country["code"],
            "sources_scraped": len(scraped),
            "sources_passed_filter": len(filtered),
            "dedup_input": len(filtered),
            "dedup_output": len(deduped),
            "dedup_merged": len(filtered) - len(deduped),
            "entities_extracted": sum(1 for r in enriched if r.get("entities")),
        }
        metadata_path = os.path.join("data", "run_metadata.json")
        os.makedirs("data", exist_ok=True)
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(run_metadata, f, indent=2)

        if send_email:
            print("Sending email digest...")
            email_text = _format_email_text(report_data)
            send_digest(email_text, "", country["name"])

        print(f"Done: {country['name']}\n")


if __name__ == "__main__":
    send_email = "--no-email" not in sys.argv
    run_pipeline(send_email=send_email)
