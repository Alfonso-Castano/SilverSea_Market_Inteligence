# pipeline/report.py — Generates the HTML report written to output/index.html
import datetime
import os
import re

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "output", "index.html")


def _slugify(heading: str) -> str:
    slug = heading.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug.strip("-")


def generate_html(report_text: str, country_name: str) -> str:
    """Wrap the plain-text report in a clean HTML page and write to output/index.html."""
    date_str = datetime.date.today().strftime("%d %B %Y")

    # Convert newlines to HTML paragraphs for basic readability
    paragraphs = ""
    in_list = False
    for line in report_text.split("\n"):
        line = line.strip()
        if not line:
            continue

        is_list_item = line.startswith("- ") or line.startswith("* ")
        if in_list and not is_list_item:
            paragraphs += "</ul>\n"
            in_list = False

        if line.startswith("###"):
            heading = line.lstrip("#").strip()
            paragraphs += f'<h3 id="{_slugify(heading)}">{heading}</h3>\n'
        elif line.startswith("##"):
            heading = line.lstrip("#").strip()
            paragraphs += f'<h2 id="{_slugify(heading)}">{heading}</h2>\n'
        elif line.startswith("#"):
            heading = line.lstrip("#").strip()
            paragraphs += f'<h1 id="{_slugify(heading)}">{heading}</h1>\n'
        elif is_list_item:
            if not in_list:
                paragraphs += "<ul>\n"
                in_list = True
            paragraphs += f"<li>{line[2:]}</li>\n"
        else:
            paragraphs += f"<p>{line}</p>\n"

    if in_list:
        paragraphs += "</ul>\n"

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
