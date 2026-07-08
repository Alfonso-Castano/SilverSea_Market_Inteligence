# app.py — Flask dashboard serving market intelligence report and AI system internals
import json
import os
import datetime
import secrets
import hmac
import re

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, session, redirect, url_for

from pipeline import source_suggestions

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
FEEDBACK_DIR = os.path.join(DATA_DIR, "feedback")
PRESENTATION_DIR = os.path.join(DATA_DIR, "presentation")

_SECRET_KEY_PATH = os.path.join(DATA_DIR, ".flask_secret_key")


def _load_or_create_secret_key():
    if os.path.exists(_SECRET_KEY_PATH):
        with open(_SECRET_KEY_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    key = secrets.token_hex(32)
    with open(_SECRET_KEY_PATH, "w", encoding="utf-8") as f:
        f.write(key)
    return key


app.secret_key = _load_or_create_secret_key()

_VIEWER_PASSWORD_PATH = os.path.join(DATA_DIR, "viewer_password.txt")


def _get_viewer_password():
    if not os.path.exists(_VIEWER_PASSWORD_PATH):
        seed = os.environ.get("VIEWER_PASSWORD", "changeme")
        with open(_VIEWER_PASSWORD_PATH, "w", encoding="utf-8") as f:
            f.write(seed)
        return seed
    with open(_VIEWER_PASSWORD_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def _set_viewer_password(new_password):
    with open(_VIEWER_PASSWORD_PATH, "w", encoding="utf-8") as f:
        f.write(new_password)


@app.before_request
def require_login():
    if request.endpoint in ("login", "static") or request.path == "/feedback":
        return None
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    return None


def _load_json(filename, default=None):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return default or {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default or {}


def _demo_mode():
    mode = request.args.get("demo", "clean")
    return mode if mode in ("clean", "feedback") else "clean"


def _domain_mode():
    domain = request.args.get("domain", "BER")
    return domain if domain in ("EDU", "BER", "GENERAL") else "BER"


@app.route("/")
def report():
    demo_mode = _demo_mode()
    domain = _domain_mode()
    report_data = _load_json(os.path.join("presentation", f"{demo_mode}_report.json"), {})
    if not report_data:
        report_data = _load_json(f"latest_report_SG_{domain}.json", {})
    if not report_data:
        report_data = _load_json("latest_report.json", {})
    return render_template("report.html", report=report_data, demo_mode=demo_mode, current_domain=domain)


@app.route("/internals")
def internals():
    demo_mode = _demo_mode()
    scores = _load_json("source_scores.json", {})
    metadata = _load_json(os.path.join("presentation", f"{demo_mode}_metadata.json"), {})
    if not metadata:
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
        demo_mode=demo_mode,
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
    raw_submitter = (data.get("submitter") or "anonymous").strip()
    submitter = re.sub(r"[^A-Za-z0-9_-]", "_", raw_submitter) or "anonymous"

    raw_rating = data.get("relevance_rating") or data.get("relevance") or 0
    try:
        relevance_rating = int(raw_rating)
    except (TypeError, ValueError):
        return {"error": "relevance_rating must be a number"}, 400

    feedback = {
        "report_date": data.get("report_date", ""),
        "relevance_rating": relevance_rating,
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

    source_name = (data.get("source_name") or "").strip()
    if source_name:
        pending_dir = os.path.join(DATA_DIR, "pending_sources")
        os.makedirs(pending_dir, exist_ok=True)
        suggestion = {
            "source_name": source_name,
            "source_url": (data.get("source_url") or "").strip(),
            "description": (data.get("source_description") or "").strip(),
            "submitted_by": submitter,
            "submitted_at": now.isoformat(),
        }
        pending_filename = f"{now.strftime('%Y%m%d_%H%M%S')}_{submitter}.json"
        with open(os.path.join(pending_dir, pending_filename), "w", encoding="utf-8") as f:
            json.dump(suggestion, f, indent=2, ensure_ascii=False)

    return "OK", 200


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        submitted = request.form.get("password", "")
        admin_password = os.environ.get("ADMIN_PASSWORD", "")
        if admin_password and hmac.compare_digest(submitted, admin_password):
            session["authenticated"] = True
            session["role"] = "admin"
            return redirect(url_for("report"))
        if hmac.compare_digest(submitted, _get_viewer_password()):
            session["authenticated"] = True
            session["role"] = "viewer"
            return redirect(url_for("report"))
        return render_template("login.html", error="Incorrect password")
    return render_template("login.html", error=None)


@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    pending = source_suggestions.list_pending()
    return render_template("admin.html", pending=pending)


@app.route("/admin/change-viewer-password", methods=["POST"])
def change_viewer_password():
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    new_password = request.form.get("new_password", "").strip()
    if new_password:
        _set_viewer_password(new_password)
    return redirect(url_for("admin"))


@app.route("/admin/sources/<filename>/approve", methods=["POST"])
def approve_source(filename):
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    sector = request.form.get("sector")
    domain = request.form.getlist("domain") or ["GENERAL"]
    country = request.form.get("country", "SG")
    source_suggestions.approve(filename, sector, domain, country_code=country)
    return redirect(url_for("admin"))


@app.route("/admin/sources/<filename>/reject", methods=["POST"])
def reject_source(filename):
    if session.get("role") != "admin":
        return redirect(url_for("login"))
    source_suggestions.reject(filename)
    return redirect(url_for("admin"))


@app.after_request
def add_cors(response):
    if request.path == "/feedback":
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


if __name__ == "__main__":
    print("Dashboard running on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
