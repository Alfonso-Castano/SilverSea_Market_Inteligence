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


FEEDBACK_FORM_TEMPLATE = """
  <hr style="margin: 48px 0 0; border: none; border-top: 1px solid #d9e2ec;" />
  <section id="feedback" style="background: #f4f9f7; border: 1px solid #d9e2ec;
            border-radius: 8px; padding: 28px 32px; margin: 32px 0 16px;">
    <h2 style="color: #0a2540; margin-top: 0;">Feedback on this report</h2>
    <form id="feedback-form" action="http://localhost:5050/feedback" method="POST">
      <input type="hidden" name="report_date" value="{report_date_iso}" />

      <div style="margin-bottom: 18px;">
        <label style="font-weight: 600; display: block; margin-bottom: 6px;">
          How useful was this report?
        </label>
        <div style="display: flex; gap: 16px; flex-wrap: wrap;">
          <label><input type="radio" name="relevance_rating" value="1" required /> 1 — Not useful</label>
          <label><input type="radio" name="relevance_rating" value="2" /> 2</label>
          <label><input type="radio" name="relevance_rating" value="3" /> 3</label>
          <label><input type="radio" name="relevance_rating" value="4" /> 4</label>
          <label><input type="radio" name="relevance_rating" value="5" /> 5 — Extremely useful</label>
        </div>
      </div>

      <div style="margin-bottom: 18px;">
        <label style="font-weight: 600; display: block; margin-bottom: 6px;" for="most_useful">
          Which signal or opportunity was most valuable?
        </label>
        <textarea id="most_useful" name="most_useful" rows="3"
          style="width: 100%; box-sizing: border-box; font-family: inherit; padding: 8px;
                 border: 1px solid #c4d3e0; border-radius: 4px;"></textarea>
      </div>

      <div style="margin-bottom: 18px;">
        <label style="font-weight: 600; display: block; margin-bottom: 6px;" for="missed_topics">
          What topics or companies should we be tracking that weren't covered?
        </label>
        <textarea id="missed_topics" name="missed_topics" rows="3"
          style="width: 100%; box-sizing: border-box; font-family: inherit; padding: 8px;
                 border: 1px solid #c4d3e0; border-radius: 4px;"></textarea>
      </div>

      <div style="margin-bottom: 18px;">
        <label style="font-weight: 600; display: block; margin-bottom: 6px;" for="priority_changes">
          Any changes to what the team should prioritize?
        </label>
        <textarea id="priority_changes" name="priority_changes" rows="3"
          style="width: 100%; box-sizing: border-box; font-family: inherit; padding: 8px;
                 border: 1px solid #c4d3e0; border-radius: 4px;"></textarea>
      </div>

      <div style="margin-bottom: 22px;">
        <label style="font-weight: 600; display: block; margin-bottom: 6px;" for="submitter">
          Your name (optional)
        </label>
        <input type="text" id="submitter" name="submitter"
          style="width: 100%; box-sizing: border-box; font-family: inherit; padding: 8px;
                 border: 1px solid #c4d3e0; border-radius: 4px;" />
      </div>

      <button type="submit"
        style="background: #2d6a4f; color: #fff; border: none; padding: 10px 24px;
               border-radius: 4px; font-size: 1em; cursor: pointer;">
        Submit Feedback
      </button>
    </form>
    <p id="feedback-thanks" style="display: none; color: #2d6a4f; font-weight: 600;">
      Thank you — your feedback has been recorded.
    </p>
  </section>
  <script>
    (function () {{
      var form = document.getElementById("feedback-form");
      var thanks = document.getElementById("feedback-thanks");
      form.addEventListener("submit", function (e) {{
        e.preventDefault();
        var data = new FormData(form);
        fetch(form.action, {{ method: "POST", body: data }})
          .finally(function () {{
            form.style.display = "none";
            thanks.style.display = "block";
          }});
      }});
    }})();
  </script>
"""


def generate_html(report_text: str, country_name: str) -> str:
    """Wrap the plain-text report in a clean HTML page and write to output/index.html."""
    date_str = datetime.date.today().strftime("%d %B %Y")
    date_iso = datetime.date.today().isoformat()

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
  {FEEDBACK_FORM_TEMPLATE.format(report_date_iso=date_iso)}
</body>
</html>"""

    os.makedirs(os.path.dirname(os.path.abspath(OUTPUT_PATH)), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"  Report written to {os.path.abspath(OUTPUT_PATH)}")
    return html
