# main.py — Runs the full market intelligence pipeline end-to-end
import sys
from config.sources import COUNTRIES
from pipeline.scraper import scrape_all
from pipeline.filter import filter_results
from pipeline.analyst import analyse
from pipeline.report import generate_html
from pipeline.emailer import send_digest


def run_pipeline(send_email: bool = True) -> None:
    active_countries = [c for c in COUNTRIES if c["active"]]
    print(f"Running pipeline for {len(active_countries)} active country/countries...\n")

    for country in active_countries:
        print(f"=== {country['name']} ({country['code']}) ===")

        print("Scraping sources...")
        scraped = scrape_all(country["sources"])

        print("Filtering content...")
        filtered = filter_results(scraped, country["keywords"])

        if not filtered:
            print("  No relevant content found — skipping LLM analysis.\n")
            continue

        print("Analysing with Claude...")
        report_text = analyse(filtered, country)

        print("Generating HTML report...")
        report_html = generate_html(report_text, country["name"])

        if send_email:
            print("Sending email digest...")
            send_digest(report_text, report_html, country["name"])

        print(f"Done: {country['name']}\n")


if __name__ == "__main__":
    # Pass --no-email to skip sending the digest (useful for local testing)
    send_email = "--no-email" not in sys.argv
    run_pipeline(send_email=send_email)
