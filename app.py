# app.py — Flask dashboard serving market intelligence report and AI system internals
import json
import os
import datetime
import secrets
import hmac
import re

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, session, redirect, url_for, send_from_directory

from pipeline import source_suggestions
from config.sources import load_sources

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
FEEDBACK_DIR = os.path.join(DATA_DIR, "feedback")
PRESENTATION_DIR = os.path.join(DATA_DIR, "presentation")
ARCHIVE_DIR = os.path.join(DATA_DIR, "archive")
_ARCHIVE_FILENAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.pdf$")
# Same 8-code whitelist used by _domain_mode() elsewhere in this file — kept as its own literal
# here rather than factored into a shared constant, matching this file's existing pattern (the
# same tuple already appears twice, in _domain_mode() and report()'s any_domain_file_exists check).
_VALID_ARCHIVE_DOMAINS = ("EDU", "BER", "GENERAL", "RCC", "HLS", "MFG", "CTE", "PSS")

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
        seed = os.environ.get("VIEWER_PASSWORD") or "Silversea"
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
    return domain if domain in ("EDU", "BER", "GENERAL", "RCC", "HLS", "MFG", "CTE", "PSS") else "BER"


def _country_mode():
    valid_codes = {c["code"] for c in load_sources()}
    country = request.args.get("country", "SG")
    return country if country in valid_codes else "SG"


DOMAINS_MERGED_INTO_GENERAL = ("RCC", "HLS", "MFG", "CTE", "PSS")


def _merge_domain_reports(report_data, country):
    """Pull RCC/HLS/MFG/CTE/PSS report files for this country (if they exist) into
    report_data for the GENERAL view, tagging each merged item with a `domain` key
    so nothing's provenance is lost. Mutates and returns report_data. Runs even if
    report_data starts as {} (GENERAL's own file absent) so extra-domain content
    isn't silently dropped."""
    merged_any = False
    last_extra_metadata = None
    for extra_domain in DOMAINS_MERGED_INTO_GENERAL:
        extra = _load_json(f"latest_report_{country}_{extra_domain}.json", {})
        if not extra:
            continue
        merged_any = True
        last_extra_metadata = extra.get("_metadata")
        report_data.setdefault("signals_by_sector", {})
        for sector, signals in extra.get("signals_by_sector", {}).items():
            report_data["signals_by_sector"].setdefault(sector, [])
            for s in signals:
                report_data["signals_by_sector"][sector].append({**s, "domain": extra_domain})
        report_data.setdefault("opportunities", [])
        report_data["opportunities"].extend(
            {**opp, "domain": extra_domain} for opp in extra.get("opportunities", [])
        )
        report_data.setdefault("competition_risks", [])
        report_data["competition_risks"].extend(
            {**risk, "domain": extra_domain} for risk in extra.get("competition_risks", [])
        )
        # data_sources must merge too — omitting it would silently break "View source"
        # links (source_urls lookup in report.html) for merged-in signals/opportunities.
        report_data.setdefault("data_sources", [])
        report_data["data_sources"].extend(extra.get("data_sources", []))

    # report.html's hero and content blocks are both gated on `report._metadata`
    # existing. If GENERAL's own file is absent but extras exist, report_data has
    # no _metadata and the page would silently show "No report available" —
    # defeating the point of merging.
    if merged_any and not report_data.get("_metadata"):
        report_data["_metadata"] = last_extra_metadata or {
            "country": country, "date": "", "date_display": ""
        }
    return report_data


_NO_SIGNAL_RE = re.compile(r"no actionable signals?", re.IGNORECASE)


def _list_archives():
    """Scan data/archive/{country}/{domain}/{date}.pdf and return a flat list of dicts (newest
    first) for the /internals archive browsing section. Returns [] if the archive dir doesn't
    exist yet (e.g. before the wrapper script has ever run) — not an error state."""
    archives = []
    if not os.path.isdir(ARCHIVE_DIR):
        return archives
    for country in sorted(os.listdir(ARCHIVE_DIR)):
        country_dir = os.path.join(ARCHIVE_DIR, country)
        if not os.path.isdir(country_dir):
            continue
        for domain in sorted(os.listdir(country_dir)):
            domain_dir = os.path.join(country_dir, domain)
            if not os.path.isdir(domain_dir):
                continue
            for filename in os.listdir(domain_dir):
                if not _ARCHIVE_FILENAME_RE.match(filename):
                    continue
                archives.append({
                    "country": country,
                    "domain": domain,
                    "date": filename[:-4],
                    "filename": filename,
                })
    archives.sort(key=lambda a: a["date"], reverse=True)
    return archives


def _strip_no_actionable_signals(report_data):
    """Drop signal/risk entries that are just the LLM's anti-hallucination abstain
    token, leaked into the final report as a fake entry instead of being omitted."""
    sbs = report_data.get("signals_by_sector")
    if sbs:
        for sector in list(sbs.keys()):
            sbs[sector] = [s for s in sbs[sector] if not _NO_SIGNAL_RE.search(s.get("signal", ""))]
    risks = report_data.get("competition_risks")
    if risks:
        report_data["competition_risks"] = [
            r for r in risks if not _NO_SIGNAL_RE.search(r.get("signal", ""))
        ]
    return report_data


@app.route("/")
def report():
    demo_mode = _demo_mode()
    domain = _domain_mode()
    country = _country_mode()
    domain_filename = f"latest_report_{country}_{domain}.json"
    report_data = _load_json(os.path.join("presentation", f"{demo_mode}_report.json"), {})
    if not report_data:
        if os.path.exists(os.path.join(DATA_DIR, domain_filename)):
            report_data = _load_json(domain_filename, {})
        else:
            # Only fall back to the pre-domain-scoping legacy report if NO domain-scoped
            # file exists yet anywhere for THIS country — never substitute a different
            # domain's or country's content for one that simply has no report yet, which
            # would silently mislabel stale cross-domain/cross-country data as belonging
            # to this one.
            any_domain_file_exists = any(
                os.path.exists(os.path.join(DATA_DIR, f"latest_report_{country}_{d}.json"))
                for d in ("EDU", "BER", "GENERAL", "RCC", "HLS", "MFG", "CTE", "PSS")  # keep in sync with _domain_mode()
            )
            if not any_domain_file_exists:
                report_data = _load_json("latest_report.json", {})
        if domain == "GENERAL":
            report_data = _merge_domain_reports(report_data, country)

    if report_data:
        report_data = _strip_no_actionable_signals(report_data)

    return render_template("report.html", report=report_data, demo_mode=demo_mode,
                            current_domain=domain, current_country=country)


@app.route("/internals")
def internals():
    demo_mode = _demo_mode()
    country = _country_mode()
    scores = _load_json("source_scores.json", {})
    metadata = _load_json(os.path.join("presentation", f"{demo_mode}_metadata.json"), {})
    if not metadata:
        country_metadata_filename = f"run_metadata_{country}.json"
        if os.path.exists(os.path.join(DATA_DIR, country_metadata_filename)):
            metadata = _load_json(country_metadata_filename, {})
        else:
            any_country_metadata_exists = any(
                os.path.exists(os.path.join(DATA_DIR, f"run_metadata_{c['code']}.json"))
                for c in load_sources()
            )
            if not any_country_metadata_exists:
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

    archives = _list_archives()

    return render_template("internals.html",
        scores=scores,
        metadata=metadata,
        collections=collections_data,
        demo_mode=demo_mode,
        current_country=country,
        archives=archives,
    )


@app.route("/internals/archive/<country>/<domain>/<filename>")
def download_archive(country, domain, filename):
    valid_codes = {c["code"] for c in load_sources()}
    if country not in valid_codes or domain not in _VALID_ARCHIVE_DOMAINS or not _ARCHIVE_FILENAME_RE.match(filename):
        return "Not found", 404
    directory = os.path.join(ARCHIVE_DIR, country, domain)
    return send_from_directory(directory, filename, as_attachment=True)


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

    raw_country = (data.get("country") or "SG").strip()
    valid_codes = {c["code"] for c in load_sources()}
    country_code = raw_country if raw_country in valid_codes else "SG"

    raw_rating = data.get("relevance_rating") or data.get("relevance") or 0
    try:
        relevance_rating = int(raw_rating)
    except (TypeError, ValueError):
        return {"error": "relevance_rating must be a number"}, 400

    source_name = (data.get("source_name") or "").strip()
    source_url = (data.get("source_url") or "").strip()
    duplicate_match = source_suggestions.find_duplicate_source(source_name, source_url) if source_name else None

    priority_changes = data.get("priority_changes", "")
    if source_name and duplicate_match:
        boost_note = (
            f"[Duplicate source suggestion] Team flagged '{source_name}' as important — "
            f"already tracked as existing source '{duplicate_match['name']}'. Treat as a "
            f"signal to weight this entity/source higher in upcoming reports."
        )
        priority_changes = f"{priority_changes}\n{boost_note}".strip() if priority_changes else boost_note
        source_suggestions.record_interest_signal(source_name, source_url, duplicate_match["name"], submitter)

    feedback = {
        "report_date": data.get("report_date", ""),
        "country": country_code,
        "relevance_rating": relevance_rating,
        "most_useful": data.get("most_useful", ""),
        "missed_topics": data.get("missed_topics", ""),
        "priority_changes": priority_changes,
        "submitter": submitter,
        "submitted_at": now.isoformat(),
    }

    os.makedirs(FEEDBACK_DIR, exist_ok=True)
    filename = f"{now.strftime('%Y%m%d_%H%M%S')}_{submitter}.json"
    with open(os.path.join(FEEDBACK_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(feedback, f, indent=2, ensure_ascii=False)

    if source_name and not duplicate_match:
        pending_dir = os.path.join(DATA_DIR, "pending_sources")
        os.makedirs(pending_dir, exist_ok=True)
        suggestion = {
            "source_name": source_name,
            "source_url": source_url,
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
    interest_signals = source_suggestions.list_interest_signals()
    countries = load_sources()
    return render_template("admin.html", pending=pending, interest_signals=interest_signals,
                            countries=countries)


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
