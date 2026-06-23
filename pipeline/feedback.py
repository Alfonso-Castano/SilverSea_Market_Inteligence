# pipeline/feedback.py — Aggregates feedback submissions into vector store digests
import json
import os
import shutil
import datetime

from groq import Groq

from pipeline.vectorstore import add_documents, FEEDBACK_DIGESTS

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
        model="llama-3.3-70b-versatile",
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
