# Feature: Local LLM Backend (Ollama + Qwen3-32B)

**Base:** 168810eeb12c6e9d5bd257c0b0df9620315d765e

## Goal

Give `pipeline/analyst.py` a config-switchable local-LLM backend (Ollama running Qwen3-32B) as an opt-in alternative to Groq, so the pipeline's LLM calls can run for free on Alfonso's own hardware instead of burning Groq's daily token quota — without changing default behavior for existing runs.

## Scope

**In scope:**
- Add a local backend option to `pipeline/analyst.py`'s LLM call sites (extraction, per-sector synthesis, summary) alongside the existing Groq path.
- `LLM_BACKEND` env var (`groq` | `local`) selects which backend runs; defaults to `groq` when unset — zero behavior change for the existing pipeline unless explicitly opted in.
- Local backend targets a locally-running Ollama server (OpenAI-compatible endpoint) serving **Qwen3-32B at Q6_K quantization**.
- Verify the local backend actually produces valid, schema-compliant JSON on real pipeline prompts (Ollama's schema-constrained structured-outputs feature, not just loose `json_object` mode) — this is the primary risk being tested.
- Stage-by-stage verification only (per CLAUDE.md's LLM-quota guidance) — this feature does not require burning Groq quota to verify, since the local path is exercised directly.

**Explicitly out of scope for this feature:**
- Changing the 3-phase extract→synthesize→summary pipeline architecture. It stays exactly as-is. (The local model removes the token-budget constraint that originally forced this architecture, but simplifying it is deliberately deferred to a later feature, once the local backend itself is proven stable across real runs.)
- AI-assisted relevance filtering (`pipeline/filter.py`). Real gap identified during discussion (pure keyword-weighted scoring today, no semantic judgment) — captured as a named future feature below, not built now.
- Automating/scheduling the pipeline to run unattended (Windows Task Scheduler, sleep/wake handling). STATE.md confirms the pipeline isn't scheduled in production yet — it's run manually — so unattended-run reliability isn't this feature's problem to solve.
- Fuzzy/semantic duplicate detection in `pipeline/source_suggestions.py`'s `find_duplicate_source()`. Identified as a real gap (exact normalized-string match only) but low-stakes and not worth AI-ifying without a demonstrated pain point.
- Any new AI use case beyond the existing 3 analyst call types (no chat interface, no agentic steps, no NL query over the internals page — explicitly pushed back on during discussion as solving problems not yet reported).

## Implementation Decisions

- **Rollout scope**: config-switchable via `LLM_BACKEND` env var; Groq stays the default. — decided by user.
- **GPU**: Nvidia RTX 5090 desktop, 32GB GDDR7 VRAM (corrected mid-discussion from an initial "RTX 5070" assumption — verify no other code/docs reference the wrong GPU model). — fact, confirmed by user.
- **Serving stack**: Ollama. Chosen over llama.cpp server (more setup work, only worth it if Ollama's structured-output reliability proves inconsistent in testing) and vLLM (poor native Windows support, WSL2-only realistically). — Claude's recommendation, accepted by user.
- **Model**: Qwen3-32B (Alibaba, Apache 2.0). Chosen over Gemma 4 31B-dense and Mistral Small 4 based on the user's own follow-up research into reasoning/analytical strength, on top of Claude's research showing all three are real, GGUF-available, and fit 32GB with headroom. — user's independent research, final call by user.
- **Quantization**: Q6_K (~23GB). Near-lossless quality with headroom for context on the 32GB card, matching the user's explicit priority of quality over speed. Q8_0 rejected (may not leave headroom for context, OOM risk); Q4_K_M rejected (trades away quality not needed given speed isn't a priority). — Claude's recommendation, accepted by user.
- **JSON reliability approach**: rely on Ollama's schema-constrained structured-outputs feature (real JSON-schema enforcement, confirmed via official Ollama docs as of mid-2026 — not just the looser `response_format: json_object` passthrough the Groq path currently uses) rather than model choice alone to guarantee valid JSON. This directly targets the known failure mode already documented in `.context/DECISIONS.md` (the 17B Groq model dropping/mangling dense multi-field JSON). — Claude's research-backed recommendation.
- **Backend selection mechanism**: env var (`LLM_BACKEND=groq|local`), read at startup alongside `GROQ_API_KEY`. Matches the project's existing env-var-driven config pattern (`VIEWER_PASSWORD`, `ADMIN_PASSWORD`, etc.). CLI flag on `main.py` was considered and rejected — would add a second place pipeline behavior gets configured from. — user's choice, Claude's option presented.
- **Filter AI enhancement**: not built in this feature. If pursued later, user's stated preference is to first evaluate whether the current keyword-weighted scoring in `pipeline/filter.py` is actually strong/insufficient before deciding whether local AI should append to it or replace it outright — not decided yet, deliberately left open for a future feature's discussion phase.
- **Architecture simplification** (removing/relaxing the 3-phase split now that local compute has no token quota): deliberately deferred. User wants the local backend proven stable on its own before changing anything else about the pipeline — "test single features out, make sure they work, then work on the next feature."
- **Branch sequencing**: `feature/001-round2-remediation` was merged to `main` before this feature's branch was cut (18 commits, clean merge, no conflicts), per explicit user confirmation. This feature branches from that up-to-date `main`.

## Global Constraints

- Existing Groq path in `pipeline/analyst.py` must continue to work byte-for-byte identically when `LLM_BACKEND` is unset or set to `groq` — this feature must not risk regressing the proven, quota-constrained production path.
- Per CLAUDE.md: verify the local backend stage-by-stage (a single extraction call, a single synthesis call, valid JSON parse) rather than requiring a full `main.py` run to claim this feature works — a full run is still worth doing eventually but isn't the evidence gate for individual tasks.
- No Groq API quota should be spent verifying the local path — the whole point is that it's free; spend real verification effort on the local calls instead.
- Match the project's boring-stack philosophy: no new frameworks/services beyond Ollama itself; the `groq` Python SDK's OpenAI-compatible interface should be reused/mirrored against Ollama's OpenAI-compatible endpoint rather than introducing a second, differently-shaped LLM client abstraction.

## Open Questions

- Exact code-level shape of the backend switch (a small `LLMClient` wrapper vs. an `if backend == "local"` branch at each of the 3 call sites) — left to the planner's judgment.
- Whether Ollama needs to be installed/pulled as part of this feature's task list, or whether that's a manual Alfonso-owned setup step before task execution begins — left to the planner to clarify, likely the latter given it's a one-time local machine setup action outside the repo.
- Context-window size to configure for Qwen3-32B in Ollama (default vs. extended) — not decided; the planner/researcher should check what's actually needed for the largest real per-sector source block before picking a number.
- Whether any other files besides `pipeline/analyst.py` reference the Groq model name/client in a way that needs mirroring for the local path (e.g. `config/models.py`'s `GROQ_MODEL` constant) — needs code-grounding during planning, not assumed here.

## Named Future Features (captured for context, not scoped here)

- **AI-assisted relevance filtering** — evaluate `pipeline/filter.py`'s current keyword-weighted scoring first; if genuinely weak, use the local model (now free to call more liberally) as either a secondary pass on borderline scores or a full replacement.
- **Pipeline architecture simplification** — once the local backend is proven stable, revisit whether the 3-phase extract→synthesize→summary split (built to work around Groq's TPM limits) can be simplified given local compute has no token quota.
