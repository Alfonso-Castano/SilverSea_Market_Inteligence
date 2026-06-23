# scripts/seed_vectorstore.py — chunk data/company_context.md and load it into ChromaDB
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipeline.vectorstore import get_client, add_documents, COMPANY_CONTEXT

CONTEXT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "company_context.md")

MAX_CHUNK_CHARS = 500
MIN_CHUNK_CHARS = 300


def split_into_sections(text):
    """Split on ## / ### headers, keeping the header with its body."""
    pattern = re.compile(r"(?m)^(#{2,3} .+)$")
    parts = pattern.split(text)
    sections = []
    current_header = None
    for part in parts:
        if pattern.match(part):
            current_header = part.strip("# ").strip()
        elif part.strip():
            sections.append((current_header or "Overview", part.strip()))
    return sections


def chunk_section(header, body):
    """Split a section body into 300-500 char chunks at paragraph boundaries."""
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for para in paragraphs:
        candidate = f"{current}\n\n{para}".strip() if current else para
        if len(candidate) > MAX_CHUNK_CHARS and current:
            chunks.append(current)
            current = para
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def build_chunks():
    with open(CONTEXT_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    sections = split_into_sections(text)
    documents = []
    metadatas = []
    for header, body in sections:
        for chunk in chunk_section(header, body):
            documents.append(chunk)
            metadatas.append({"section": header, "source": "company_context"})
    return documents, metadatas


def seed():
    client = get_client()
    try:
        client.delete_collection(COMPANY_CONTEXT)
    except Exception:
        pass

    documents, metadatas = build_chunks()
    add_documents(COMPANY_CONTEXT, documents, metadatas)
    print(f"Seeded {len(documents)} chunks into '{COMPANY_CONTEXT}' collection.")


if __name__ == "__main__":
    seed()
