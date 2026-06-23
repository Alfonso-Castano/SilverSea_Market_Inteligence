# scripts/feedback_server.py — Minimal Flask endpoint for feedback form submissions
import json
import os
import datetime

from flask import Flask, request

app = Flask(__name__)

FEEDBACK_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "feedback")


@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/feedback", methods=["POST", "OPTIONS"])
def receive_feedback():
    if request.method == "OPTIONS":
        return "", 204

    now = datetime.datetime.now(datetime.timezone.utc)
    submitter = (request.form.get("submitter") or "anonymous").strip().replace(" ", "_")

    feedback = {
        "report_date": request.form.get("report_date", ""),
        "relevance_rating": int(request.form.get("relevance_rating", 0)),
        "most_useful": request.form.get("most_useful", ""),
        "missed_topics": request.form.get("missed_topics", ""),
        "priority_changes": request.form.get("priority_changes", ""),
        "submitter": submitter,
        "submitted_at": now.isoformat(),
    }

    os.makedirs(FEEDBACK_DIR, exist_ok=True)
    filename = f"{now.strftime('%Y%m%d_%H%M%S')}_{submitter}.json"
    filepath = os.path.join(FEEDBACK_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(feedback, f, indent=2, ensure_ascii=False)

    return "OK", 200


if __name__ == "__main__":
    print(f"Feedback server running on http://localhost:5050")
    print(f"Saving to: {FEEDBACK_DIR}")
    app.run(host="0.0.0.0", port=5050, debug=False)
