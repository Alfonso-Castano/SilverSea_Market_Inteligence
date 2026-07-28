# scripts/daily_pipeline.py — Loops all 9 SG/VN/MY x EDU/BER/GENERAL combinations sequentially,
# invoking main.py as a subprocess per combination (matching its existing CLI invocation shape),
# archiving each successful combination's report to PDF, and logging per-combination outcomes.
# Sequential, not parallel, by design — avoids concurrent ChromaDB writes across processes.
import datetime
import os
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(PROJECT_ROOT, "data", "logs")
LOG_PATH = os.path.join(LOG_DIR, "daily_pipeline.log")

COUNTRIES = ("SG", "VN", "MY")
DOMAINS = ("EDU", "BER", "GENERAL")
COMBINATIONS = [(c, d) for c in COUNTRIES for d in DOMAINS]


def _log(line: str) -> None:
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {line}\n")
    print(line)


def run_all() -> None:
    for country, domain in COMBINATIONS:
        try:
            result = subprocess.run(
                [sys.executable, "main.py", f"--country={country}", f"--domain={domain}", "--no-email"],
                cwd=PROJECT_ROOT,
                check=False,
            )
        except Exception as e:
            _log(f"{country} {domain} FAILED (subprocess error: {e})")
            continue

        if result.returncode != 0:
            _log(f"{country} {domain} FAILED (main.py exit code {result.returncode})")
            continue

        try:
            from pipeline.archive import archive_report_pdf
            archive_path = archive_report_pdf(country, domain)
            _log(f"{country} {domain} SUCCESS archived={archive_path}")
        except Exception as e:
            _log(f"{country} {domain} SUCCESS archive_failed=({e})")


if __name__ == "__main__":
    run_all()
