# pipeline/dedup.py — Semantic deduplication of same-story signals across sources
import numpy as np
from sentence_transformers import SentenceTransformer

EMBED_MODEL = "all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.85
COMPARE_CHARS = 300

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def deduplicate(filtered_results: list) -> list:
    """
    Merge duplicate signals across sources using embedding similarity.

    Compares the first 300 chars of each result's content. Pairs with cosine
    similarity > 0.85 are merged into a single entry keyed on the longer content.
    """
    if len(filtered_results) <= 1:
        return filtered_results

    model = _get_model()
    snippets = [r["content"][:COMPARE_CHARS] for r in filtered_results]
    embeddings = model.encode(snippets, normalize_embeddings=True)

    merged_into = {}  # index -> index of the primary it was merged into
    n = len(filtered_results)
    for i in range(n):
        if i in merged_into:
            continue
        for j in range(i + 1, n):
            if j in merged_into:
                continue
            similarity = float(np.dot(embeddings[i], embeddings[j]))
            if similarity > SIMILARITY_THRESHOLD:
                merged_into[j] = i

    groups = {}
    for idx in range(n):
        primary = idx
        while primary in merged_into:
            primary = merged_into[primary]
        groups.setdefault(primary, []).append(idx)

    deduplicated = []
    for primary_idx, member_idxs in groups.items():
        if len(member_idxs) == 1:
            deduplicated.append(filtered_results[primary_idx])
            continue

        members = sorted(
            (filtered_results[i] for i in member_idxs),
            key=lambda r: len(r["content"]),
            reverse=True,
        )
        primary = members[0]
        merged = dict(primary)
        merged["urls"] = [m["url"] for m in members]
        merged["names"] = [m["name"] for m in members]
        merged["sources_count"] = len(members)
        merged.pop("url", None)
        merged.pop("name", None)
        deduplicated.append(merged)

    removed = n - len(deduplicated)
    if removed:
        print(f"  Dedup: merged {removed} duplicate signal(s), {len(deduplicated)} remain")
    return deduplicated
