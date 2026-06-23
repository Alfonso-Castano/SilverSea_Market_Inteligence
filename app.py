# app.py — Flask dashboard serving market intelligence report and AI system internals
import json
import os
import datetime

from flask import Flask, render_template, request

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
FEEDBACK_DIR = os.path.join(DATA_DIR, "feedback")


def _load_json(filename, default=None):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return default or {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default or {}


@app.route("/")
def report():
    report_data = _load_json("latest_report.json", {})
    return render_template("report.html", report=report_data)


@app.route("/internals")
def internals():
    scores = _load_json("source_scores.json", {})
    metadata = _load_json("run_metadata.json", {})

    collections_data = {}
    try:
        from pipeline.vectorstore import get_collection, COMPANY_CONTEXT, REPORT_HISTORY, FEEDBACK_DIGESTS
        for name in [COMPANY_CONTEXT, REPORT_HISTORY, FEEDBACK_DIGESTS]:
            col = get_collection(name)
            result = col.get(limit=20, include=["documents", "metadatas"])
            collections_data[name] = {
                "documents": result.get("documents", []),
                "metadatas": result.get("metadatas", []),
                "ids": result.get("ids", []),
                "count": col.count(),
            }
    except Exception as e:
        collections_data = {"error": str(e)}

    return render_template("internals.html",
        scores=scores,
        metadata=metadata,
        collections=collections_data,
    )


@app.route("/feedback", methods=["POST", "OPTIONS"])
def receive_feedback():
    if request.method == "OPTIONS":
        return "", 204

    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    now = datetime.datetime.now(datetime.timezone.utc)
    submitter = (data.get("submitter") or "anonymous").strip().replace(" ", "_")

    feedback = {
        "report_date": data.get("report_date", ""),
        "relevance_rating": int(data.get("relevance_rating") or data.get("relevance") or 0),
        "most_useful": data.get("most_useful", ""),
        "missed_topics": data.get("missed_topics", ""),
        "priority_changes": data.get("priority_changes", ""),
        "submitter": submitter,
        "submitted_at": now.isoformat(),
    }

    os.makedirs(FEEDBACK_DIR, exist_ok=True)
    filename = f"{now.strftime('%Y%m%d_%H%M%S')}_{submitter}.json"
    with open(os.path.join(FEEDBACK_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(feedback, f, indent=2, ensure_ascii=False)

    return "OK", 200


@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


if __name__ == "__main__":
    print("Dashboard running on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
