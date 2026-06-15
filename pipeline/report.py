# pipeline/report.py — Generates the HTML report written to output/index.html
import datetime
import os

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "output", "index.html")


def generate_html(report_text: str, country_name: str) -> str:
    """Wrap the plain-text report in a clean HTML page and write to output/index.html."""
    date_str = datetime.date.today().strftime("%d %B %Y")

    # Convert newlines to HTML paragraphs for basic readability
    paragraphs = ""
    for line in report_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("###"):
            paragraphs += f"<h3>{line.lstrip('#').strip()}</h3>\n"
        elif line.startswith("##"):
            paragraphs += f"<h2>{line.lstrip('#').strip()}</h2>\n"
        elif line.startswith("#"):
            paragraphs += f"<h1>{line.lstrip('#').strip()}</h1>\n"
        elif line.startswith("- ") or line.startswith("* "):
            paragraphs += f"<li>{line[2:]}</li>\n"
        else:
            paragraphs += f"<p>{line}</p>\n"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Silversea Market Intelligence — {country_name} — {date_str}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
           max-width: 860px; margin: 40px auto; padding: 0 24px;
           color: #1a1a1a; line-height: 1.6; }}
    h1 {{ color: #0a2540; border-bottom: 2px solid #0a2540; padding-bottom: 8px; }}
    h2 {{ color: #0a2540; margin-top: 32px; }}
    h3 {{ color: #2d6a4f; }}
    li {{ margin: 4px 0; }}
    .meta {{ color: #666; font-size: 0.9em; margin-bottom: 32px; }}
  </style>
</head>
<body>
  <h1>Silversea Media — Market Intelligence Report</h1>
  <p class="meta">{country_name} &nbsp;|&nbsp; {date_str} &nbsp;|&nbsp; Auto-generated</p>
  {paragraphs}
</body>
</html>"""

    os.makedirs(os.path.dirname(os.path.abspath(OUTPUT_PATH)), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  Report written to {os.path.abspath(OUTPUT_PATH)}")
    return html
