# pipeline/weekly.py — Compresses 7 daily reports into one weekly summary
import os
import datetime

from groq import Groq

from pipeline.vectorstore import query, add_documents, delete_documents, get_collection, REPORT_HISTORY

WEEKLY_PROMPT = """You are summarizing a week of daily market intelligence reports for Silversea Media
(digital twin & immersive tech company, Singapore).

Compress these {count} daily reports into ONE weekly intelligence summary. Structure:
1. TOP SIGNALS THIS WEEK — 5-7 most important developments
2. OPPORTUNITIES UPDATE — any scored opportunities, status changes
3. SECTOR TRENDS — what's moving in each sector (gov, associations, customers, competitors)
4. RECOMMENDED ACTIONS — 2-3 things the BD team should do this week

Be concise. This replaces the daily reports in the team's memory.

Daily reports:
{reports}"""


def generate_weekly_summary() -> str:
    """Retrieve recent daily reports, compress into weekly summary, update vector store."""
    collection = get_collection(REPORT_HISTORY)
    count = collection.count()
    if count == 0:
        print("No daily reports in vector store — skipping weekly summary.")
        return ""

    results = collection.get(limit=min(count, 14), include=["documents", "metadatas"])
    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    ids = results.get("ids", [])

    if not documents:
        print("No daily reports found — skipping weekly summary.")
        return ""

    today = datetime.date.today()
    week_ago = today - datetime.timedelta(days=7)

    weekly_docs = []
    weekly_ids = []
    for doc, meta, doc_id in zip(documents, metadatas, ids):
        date_str = (meta or {}).get("date", "")
        try:
            doc_date = datetime.date.fromisoformat(date_str)
            if doc_date >= week_ago:
                weekly_docs.append(doc)
                weekly_ids.append(doc_id)
        except (ValueError, TypeError):
            weekly_docs.append(doc)
            weekly_ids.append(doc_id)

    if not weekly_docs:
        print("No reports from the last 7 days — skipping.")
        return ""

    reports_text = "\n\n---\n\n".join(weekly_docs)

    client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))
    if not client.api_key:
        print("Weekly summary skipped — no GROQ_API_KEY")
        return ""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": WEEKLY_PROMPT.format(count=len(weekly_docs), reports=reports_text)}],
        max_tokens=2048,
    )

    summary = response.choices[0].message.content

    delete_documents(REPORT_HISTORY, weekly_ids)

    add_documents(
        REPORT_HISTORY,
        [summary],
        metadatas=[{
            "date": today.isoformat(),
            "type": "weekly_summary",
            "covers_from": week_ago.isoformat(),
            "covers_to": today.isoformat(),
            "daily_count": str(len(weekly_docs)),
        }],
    )

    print(f"  Weekly summary: compressed {len(weekly_docs)} daily reports into 1 summary")
    return summary


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    summary = generate_weekly_summary()
    if summary:
        print("\n" + summary)
