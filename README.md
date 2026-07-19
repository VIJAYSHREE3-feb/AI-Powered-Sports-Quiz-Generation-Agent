# 🏆 AI-Powered Sports Quiz Generator (RAG Agent)

**Live demo:** https://ai-powered-sports-quiz-generation-agent-yc8vqwnnnth2ezvyecwsya.streamlit.app/

A Streamlit web app that generates fact-grounded, multiple-choice sports quizzes
using **Retrieval-Augmented Generation (RAG)**: it blends a local **ChromaDB**
vector store of historic sports facts with **live web search** results
(via `ddgs`), then asks an LLM (**Google Gemini**, free tier) to write quiz
questions using *only* that retrieved context.

---

## 1. What this project does

- Lets a user pick a **sport** and **difficulty** in a sidebar.
- Retrieves matching facts from a local vector database (`ChromaDB`).
- Retrieves live/recent news snippets from the web (`ddgs`).
- Sends both as grounding **context** to an LLM, which is instructed not to
  hallucinate and to only use the given facts.
- Displays 3 multiple-choice questions with answers + explanations, plus an
  expandable panel showing the exact context used (for transparency/audit).
- Shows a themed image for the selected sport alongside the quiz, in a clean
  two-column layout — the image never overlaps or obscures any text.

---

## 2. Prerequisites

- **Python 3.9, 3.10, or 3.11** (avoid 3.12+ — ChromaDB's dependencies compile
  most reliably on these versions).
- A **free Google Gemini API key** from
  [Google AI Studio](https://aistudio.google.com/apikey) — no credit card
  required. Sign in with any Google account, click **Create API key**, and
  copy it.

---

## 3. Folder structure

```
sports-quiz-agent/
│
├── .env                       # YOU create this — holds your real API key (not committed)
├── .env.example                # Template showing the expected variable name
├── .gitignore                  # Prevents .env, venv/, chroma_db/ from being committed
├── requirements.txt             # Dependencies
├── README.md                    # This file
│
├── data/
│   └── sports_facts.json        # Local offline knowledge base (16 facts, 8 sports)
│
├── chroma_db/                    # Auto-created by ChromaDB the first time you run the app
│
├── assets/
│   └── backgrounds/               # Per-sport images shown alongside the quiz
│       ├── cricket.jpg
│       ├── football.jpg
│       ├── badminton.jpg
│       ├── tennis.jpg
│       ├── basketball.jpg
│       ├── hockey.jpg
│       ├── formula1.jpg
│       └── athletics.jpg
│
├── src/
│   ├── __init__.py
│   ├── config.py                 # Loads Gemini API key from .env or Streamlit secrets
│   ├── database.py                # ChromaDB insert/query logic (+ sqlite compatibility fix)
│   ├── search.py                   # Live web search logic (ddgs, with graceful fallback)
│   └── generator.py                 # RAG orchestration + LLM prompt + Gemini call
│
└── app.py                            # Streamlit front-end (run this file)
```

---

## 4. Step-by-step setup (run these in your terminal)

```bash
# 1. Enter the project folder (skip if you're already there)
cd sports-quiz-agent

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Add your API key
cp .env.example .env          # Windows: copy .env.example .env
# then open .env and paste your real Gemini key:
# GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# 5. Run the app
streamlit run app.py
```

Streamlit will open a browser tab (usually `http://localhost:8501`). The first
run automatically builds the `chroma_db/` folder and vectorizes
`data/sports_facts.json` — you'll see a console message confirming how many
facts were stored (16, across 8 sports).

---

## 5. Using the app

1. In the sidebar, choose a **Sport** (Cricket, Football, Badminton, Tennis,
   Basketball, Hockey, Formula 1, Athletics).
2. Choose a **Difficulty** (Easy / Medium / Hard).
3. Click **Generate Fresh Quiz**.
4. The app fetches ChromaDB facts + a live web search, sends both to Gemini,
   and displays the formatted quiz next to a themed image for that sport.
5. Expand **🔍 Inspect Ground Truth** to see exactly which context grounded
   the questions — this is your proof the app isn't hallucinating.

---

## 6. Adding more knowledge

To extend the offline knowledge base, add more entries to
`data/sports_facts.json` in this shape:

```json
{
  "sport": "Tennis",
  "fact": "The first Wimbledon Championship was held in 1877, and Spencer Gore won the inaugural gentlemen's singles title."
}
```

If you add a brand-new sport (not already in the list), also add it to the
`SPORT_IMAGES` dictionary and the sidebar dropdown list in `app.py`, and drop
a matching image into `assets/backgrounds/`.

Then delete the `chroma_db/` folder (so it rebuilds) and re-run the app —
`setup_and_populate_db()` only populates when the collection is empty.

---

## 7. Troubleshooting

| Problem | Fix |
|---|---|
| `sqlite3` version error on Linux (e.g. Streamlit Cloud) | Already handled: `src/database.py` tries `pysqlite3-binary` and falls back safely if it's not installed (e.g. on macOS locally) |
| API key not found / warning on startup | Confirm `.env` exists in the project root and contains `GEMINI_API_KEY=...` (no quotes, no spaces around `=`) |
| `404 NOT_FOUND` on a Gemini model name | Google periodically renames/retires model IDs. The code uses `gemini-flash-latest`, a maintained alias that always points to the current recommended Flash model — update it in `src/generator.py` if Google changes this again |
| `429 RESOURCE_EXHAUSTED` | You've hit the free tier's per-minute or per-day cap. Wait a minute, or check quota at [Google AI Studio](https://aistudio.google.com). Don't enable billing just to fix this — it removes the free tier entirely |
| Quiz text doesn't parse into clean Q/A blocks | The LLM occasionally varies formatting. Tighten the prompt in `src/generator.py`, or request a JSON-structured response for guaranteed parsing |
| Live web search section comes back empty | Handled gracefully — `search.py` shows a clear fallback message if `ddgs` returns zero results (common rate-limiting behavior), and the quiz still generates from offline facts alone |
| Background/side image not showing | Confirm the file exists at the exact path in `assets/backgrounds/` referenced by `SPORT_IMAGES` in `app.py` — filenames are case-sensitive |
| Keys accidentally pushed to GitHub | Revoke the leaked key immediately at [Google AI Studio](https://aistudio.google.com/apikey) and generate a new one. Confirm `.env` is listed in `.gitignore` (it already is here) |
| `git push` rejected (non-fast-forward / diverged branches) | Run `git config pull.rebase false`, then `git pull origin main`, resolve/commit any merge, then `git push` again |

---

## 8. Using OpenAI instead of Gemini (optional swap)

If you'd rather use OpenAI (e.g. gpt-4o) instead of the free Gemini tier:

```bash
pip install openai
```

Then in `src/generator.py`, replace the `genai.Client` block with the
`OpenAI` client and its `chat.completions.create` call, keeping the same
`system_instruction` + `user_prompt` structure, and update `src/config.py`
to load `OPENAI_API_KEY` instead. The RAG logic (`database.py`, `search.py`)
stays identical — only the final LLM call changes. Note OpenAI requires a
funded billing account; it has no free API tier.

---

## 9. Deployment (Streamlit Community Cloud)

This app is deployed at:
**https://ai-powered-sports-quiz-generation-agent-yc8vqwnnnth2ezvyecwsya.streamlit.app/**

To deploy your own copy:

1. Push this project to a public GitHub repo (`.env` excluded via `.gitignore`).
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
3. Click **New app** → select your repo → branch `main` → main file `app.py`.
4. Under **Advanced settings → Secrets**, add:
   ```
   GEMINI_API_KEY = "your-real-key-here"
   ```
5. Click **Deploy**. Streamlit Cloud auto-redeploys on every push to `main`.
