# Silversea Market Intelligence System

Automated daily market intelligence for Silversea Media's BD/sales team. Scrapes ~57 sources across Singapore's built environment sector, runs AI-powered extraction and synthesis, and serves an interactive dashboard with 65+ signals per run.

## Quick Start — View the Dashboard

You only need Flask installed to see the report:

```bash
git clone https://github.com/Alfonso-Castano/SilverSea_Market_Inteligence.git
cd SilverSea_Market_Inteligence
pip install flask
py app.py
```

Open **http://localhost:5000** in your browser. The dashboard renders from pre-generated report data — no API keys or pipeline run needed.

## Dashboard

**Report page** (`/`) — Market intelligence signals grouped by entity within 5 color-coded sectors. Features: collapsible entity groups, signal spotlight (click any card), dark/light mode toggle, scroll progress bar, source links on every signal card.

**Internals page** (`/internals`) — AI system observability: vector store contents, source quality scores, feedback digests, run metadata.

**Feedback form** — Embedded at the bottom of the report page. Submissions are aggregated and fed back into the AI system to shape future reports.

## Architecture

```
Scraper (57 sources, 5 sectors)
  → Keyword Filter (priority + general tiered weighting)
  → Per-Sector Extraction (6 LLM calls — one per sector)
  → Per-Sector Synthesis (6 LLM calls — extraction text → structured JSON)
  → Summary Call (1 LLM call — executive summary + opportunities)
  → data/latest_report.json
  → Flask app serves dashboard
```

**Stack:** Python, Flask + Jinja2, Tailwind CSS (CDN), Groq API (Llama 4 Scout 17B), ChromaDB

**Sectors:** Government & Agencies, Industry Associations, Customers, Partners, Competitors

## Running the Full Pipeline

Requires a `.env` file:

```
GROQ_API_KEY=your_groq_api_key
```

Then:

```bash
pip install -r requirements.txt
py main.py
```

Takes ~30 seconds, uses ~15-20k Groq tokens per run. Output overwrites `data/latest_report.json`, which the Flask app reads on each request.

## Environment Variables

| Variable | Required For | Description |
|---|---|---|
| `GROQ_API_KEY` | Pipeline only | Groq API key ([free tier](https://console.groq.com)) |
| `LLM_BACKEND` | Pipeline only | `groq` (default) or `local` — selects which LLM backend `pipeline/analyst.py` calls. `local` requires a locally-running Ollama server serving Qwen3-32B at Q6_K quantization (see "Local LLM Setup" below) |
| `LOCAL_LLM_MODEL` | Local backend only | Ollama tag the Q6_K model was registered under (default `qwen3-32b-q6k`) |
| `LOCAL_LLM_NUM_CTX` | Local backend only | Context window size passed to Ollama (default `32768`) |
| `GMAIL_USER` | Email only | Sender Gmail address |
| `GMAIL_APP_PASSWORD` | Email only | Gmail app password |
| `RECIPIENT_EMAILS` | Email only | Comma-separated recipient list |

None of these are needed to view the dashboard.

## Local LLM Setup (Optional)

Running the pipeline with a locally-hosted LLM (Ollama + Qwen3-32B) is a free alternative to Groq. This section walks through setup on a fresh Windows machine.

**Prerequisite hardware/software:** This setup requires a GPU with substantial VRAM headroom — the Qwen3-32B Q6_K quantization weights approximately 23GB. This path was developed against a 32GB RTX 5090. You'll also need Windows with Ollama installed.

**Step 1 — Install Ollama**
Download and install Ollama from [ollama.com](https://ollama.com) for Windows. After installation, confirm it's working by opening a terminal and running:
```bash
ollama --version
```

**Step 2 — Download the Q6_K GGUF**
Download `Qwen3-32B-Q6_K.gguf` from [bartowski/Qwen3-32B-GGUF](https://huggingface.co/bartowski/Qwen3-32B-GGUF) on Hugging Face. This is a large manual download (~23GB); note that this is not something to script or automate — download it directly and save it locally.

**Step 3 — Register it with Ollama**
Create a one-line text file called `Modelfile` in the same directory where you downloaded the GGUF. Its contents should be:
```
FROM ./Qwen3-32B-Q6_K.gguf
```
Then, in that same directory, run:
```bash
ollama create qwen3-32b-q6k -f Modelfile
```
Confirm the registration succeeded by running:
```bash
ollama list
```
You should see `qwen3-32b-q6k` in the list.

**Step 4 — Clone this repo and install Python deps**
```bash
git clone https://github.com/Alfonso-Castano/SilverSea_Market_Inteligence.git
cd SilverSea_Market_Inteligence
pip install -r requirements.txt
```

**Step 5 — Set `LLM_BACKEND=local` in `.env`**
Create or edit your `.env` file to include:
```
LLM_BACKEND=local
```
(You do not need `GROQ_API_KEY` when running with a local backend.)

**Step 6 — Verify the backend works**
Run the local-backend smoke test:
```bash
py -m pytest tests/test_local_backend_smoke.py -v
```
Confirm it passes with real schema-compliant JSON output. If it is skipped, step 2 or 3 was not completed correctly — check that Ollama can serve the model.

**Step 7 — Run the full pipeline**
```bash
py main.py --domain=BER --country=SG
```
(Or whichever domain/country suits your needs.) The pipeline will call the local Ollama server for extraction and synthesis.

**Overriding quantization or context window:**
If your setup differs (e.g., a different quantization was chosen, or VRAM headroom is tighter than expected), you can override the model tag and context window via environment variables:
```
LOCAL_LLM_MODEL=qwen3-32b-q8      # if you used Q8 instead
LOCAL_LLM_NUM_CTX=16384             # if you need a smaller context window
```
