# pipeline/feedback.py — Aggregates feedback submissions into vector store digests
import json
import os
import shutil
import datetime

from groq import Groq

from config.models import GROQ_MODEL
from pipeline.vectorstore import add_documents, delete_documents, get_collection, FEEDBACK_DIGESTS

FEEDBACK_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "feedback")
PROCESSED_DIR = os.path.join(FEEDBACK_DIR, "processed")

SUMMARIZE_PROMPT = """Summarize the following team feedback into a concise priority digest (3-5 bullets).
Focus on: what topics the team wants covered, what they found useful, what they want deprioritized.
Output ONLY the bullet points — no preamble.

Feedback submissions:
{feedback_text}"""


def aggregate_feedback() -> None:
    """Read unprocessed feedback, summarize via LLM, store digest in vector store."""
    if not os.path.isdir(FEEDBACK_DIR):
        return

    json_files = [f for f in os.listdir(FEEDBACK_DIR) if f.endswith(".json")]
    if not json_files:
        return

    submissions = []
    for filename in json_files:
        filepath = os.path.join(FEEDBACK_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8-sig") as f:
                submissions.append(json.load(f))
        except (json.JSONDecodeError, OSError):
            continue

    if not submissions:
        return

    feedback_text = "\n\n".join(
        f"Rating: {s.get('relevance_rating', '?')}/5\n"
        f"Most useful: {s.get('most_useful', 'N/A')}\n"
        f"Missed topics: {s.get('missed_topics', 'N/A')}\n"
        f"Priority changes: {s.get('priority_changes', 'N/A')}"
        for s in submissions
    )

    client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
    if not client.api_key:
        print("  Feedback aggregation skipped — no GROQ_API_KEY")
        return

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": SUMMARIZE_PROMPT.format(feedback_text=feedback_text)}],
        max_tokens=512,
    )

    digest = response.choices[0].message.content
    add_documents(
        FEEDBACK_DIGESTS,
        [digest],
        metadatas=[{
            "date": datetime.date.today().isoformat(),
            "submissions_count": str(len(submissions)),
        }],
    )

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    for filename in json_files:
        shutil.move(os.path.join(FEEDBACK_DIR, filename), os.path.join(PROCESSED_DIR, filename))

    print(f"  Feedback: aggregated {len(submissions)} submission(s) into vector store digest")


CONSOLIDATION_PROMPT = """Compress these {count} feedback digests into ONE consolidated priority summary.
Preserve any recurring themes, drop one-off or superseded requests.
Output 4-6 bullets, no preamble.

Digests:
{digests_text}"""


def consolidate_feedback_digests(max_digests: int = 10) -> None:
    """Merge oldest feedback digests when collection exceeds cap.
    Mirrors pipeline/weekly.py's delete-then-replace pattern."""
    # placeholder cap, untuned — revisit with real usage data
    collection = get_collection(FEEDBACK_DIGESTS)
    count = collection.count()
    if count <= max_digests:
        return

    results = collection.get(include=["documents", "metadatas"])
    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    ids = results.get("ids", [])

    # Sort by date, oldest first
    paired = list(zip(ids, documents, metadatas))
    paired.sort(key=lambda x: (x[2] or {}).get("date", ""))

    # Consolidate just enough to get back under the cap
    n_to_consolidate = count - max_digests + 1
    old_ids = [p[0] for p in paired[:n_to_consolidate]]
    old_docs = [p[1] for p in paired[:n_to_consolidate]]

    digests_text = "\n\n---\n\n".join(old_docs)

    client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
    if not client.api_key:
        print("  Feedback consolidation skipped — no GROQ_API_KEY")
        return

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": CONSOLIDATION_PROMPT.format(
            count=len(old_docs), digests_text=digests_text
        )}],
        max_tokens=512,
    )

    consolidated = response.choices[0].message.content

    delete_documents(FEEDBACK_DIGESTS, old_ids)
    add_documents(
        FEEDBACK_DIGESTS,
        [consolidated],
        metadatas=[{
            "date": datetime.date.today().isoformat(),
            "type": "consolidated",
            "source_count": str(len(old_ids)),
        }],
    )

    print(f"  Feedback: consolidated {len(old_ids)} old digests into 1 summary")
