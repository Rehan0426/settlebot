# SettleBot

AI settlement Q&A assistant for Razorpay merchants. Ask in English or Hinglish about settlements, fees, GST, refunds and date ranges ("last financial year", "Q2 2025", "pichle mahine") and get answers grounded in live settlement data.

## Requirements

- Python 3.10+
- A Gemini API key (primary) and/or a Groq API key (fallback)

## Setup

```bash
git clone <your-repo-url>
cd settlebot

python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env      # Windows: copy .env.example .env
# open .env and paste your GEMINI_API_KEY and/or GROQ_API_KEY
```

`.env` is git-ignored. Never commit real API keys.

### Model order

SettleBot tries providers and models in this order and shows the one that answered in a small badge under each reply:

1. **Google Gemini** (`GEMINI_API_KEY`): `gemini-3.6-flash`, then the other supported Gemini models
2. **Groq** (`GROQ_API_KEY`): `qwen/qwen3.8-27b`, then `openai/gpt-oss-120b`

To change the Groq order or add a model, set `GROQ_MODELS` in `.env` as a comma-separated list. Model IDs must match Groq's catalogue exactly.

## Run

```bash
python app.py
```

Open http://localhost:5001. Synthetic settlement data (`settlements.csv`) is generated automatically on first start.

## Evaluate

```bash
python eval_harness.py
```

or hit `GET /api/eval` while the app is running.

## Project layout

| File | Purpose |
|---|---|
| `app.py` | Flask server, `/`, `/api/chat`, `/api/eval` |
| `agent.py` | LLM orchestration, tool calling, error classification |
| `tools.py` | Settlement lookups and natural-language date resolution |
| `memory.py` | Per-session conversation memory |
| `generate_data.py` | Synthetic settlement data generator |
| `eval_harness.py` | Accuracy evaluation over 50 sample questions |
| `templates/index.html` | Chat UI |
| `stitchui/` | Design reference (Stitch export) |

## Deploying

Set `GEMINI_API_KEY` / `GROQ_API_KEY` as environment variables on your host (Render, Railway, Fly.io, a VPS, etc.). Do not upload your `.env` file. For production, run behind a WSGI server, for example:

```bash
pip install gunicorn
gunicorn -b 0.0.0.0:5001 app:app
```
