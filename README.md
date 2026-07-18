# 🏆 AI-Powered Sports Quiz Generator (RAG Agent)

A Streamlit web app that generates fact-grounded, multiple-choice sports quizzes
using **Retrieval-Augmented Generation (RAG)**: it blends a local **ChromaDB**
vector store of historic sports facts with **live DuckDuckGo web search** results,
then asks an LLM (OpenAI) to write quiz questions using *only* that retrieved context.

---

## 1. What this project does

- Lets a user pick a **sport** and **difficulty** in a sidebar.
- Retrieves matching facts from a local vector database (`ChromaDB`).
- Retrieves live/recent news snippets from the web (`duckduckgo-search`).
- Sends both as grounding **context** to an LLM, which is instructed not to
  hallucinate and to only use the given facts.
- Displays 3 multiple-choice questions with answers + explanations in the
  Streamlit UI, plus an expandable panel showing the exact context used
  (for transparency/audit).

---

## 2. Prerequisites

- **Python 3.9, 3.10, or 3.11** (avoid 3.12+ — ChromaDB's dependencies compile
  most reliably on these versions).
- An **OpenAI API key** (or swap in Google Gemini's `google-genai` SDK if you prefer —
  see "Using Gemini instead" below).

---

## 3. Folder structure

```
sports-quiz-agent/
│
├── .env                  # YOU create this — holds your real API key (not committed)
├── .env.example           # Template showing the expected variable name
├── .gitignore             # Prevents .env, venv/, chroma_db/ from being committed
├── requirements.txt        # Dependencies
├── README.md               # This file
│
├── data/
│   └── sports_facts.json   # Local offline knowledge base
│
├── chroma_db/               # Auto-created by ChromaDB the first time you run the app
│
├── src/
│   ├── __init__.py
│   ├── config.py            # Loads API key from .env
│   ├── database.py          # ChromaDB insert/query logic
│   ├── search.py             # DuckDuckGo live web search logic
│   └── generator.py           # RAG orchestration + LLM prompt + call
│
└── app.py                     # Streamlit front-end (run this file)
```

---

## 4. Step-by-step setup (run these in your terminal)

```bash
# 1. Create and enter the project folder (skip if you already have the files)
cd sports-quiz-agent

# 2. Create a virtual environment
python -m venv venv          # Windows: python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Add your API key
cp .env.example .env          # Windows: copy .env.example .env
# then open .env and paste your real key:
# OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxx

# 5. Run the app
streamlit run app.py
```

Streamlit will open a browser tab (usually `http://localhost:8501`). The first
run automatically builds the `chroma_db/` folder and vectorizes
`data/sports_facts.json` — you'll see a console message confirming how many
facts were stored.

---

## 5. Using the app

1. In the sidebar, choose a **Sport** (Cricket, Football, Badminton — expand
   this list in `app.py` and `data/sports_facts.json` if you want more).
2. Choose a **Difficulty** (Easy / Medium / Hard).
3. Click **Generate Fresh Quiz**.
4. The app fetches ChromaDB facts + a live web search, sends both to the LLM,
   and displays the formatted quiz.
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

Then delete the `chroma_db/` folder (so it rebuilds) and re-run the app —
or restart the Streamlit process, since `setup_and_populate_db()` only
populates when the collection is empty.

---

## 7. Troubleshooting

| Problem | Fix |
|---|---|
| `sqlite3` version error on Windows/Linux | `pip install pysqlite3-binary`, then uncomment the 3-line sqlite patch at the top of `src/database.py` |
| API key not found / warning on startup | Confirm `.env` exists in the project root and contains `OPENAI_API_KEY=...` (no quotes, no spaces around `=`) |
| Quiz text doesn't parse into clean Q/A blocks | The LLM occasionally varies formatting. Tighten the prompt in `src/generator.py`, or switch to `response_format={"type": "json_object"}` (JSON mode) for guaranteed structure |
| DuckDuckGo search fails / returns nothing | This is handled gracefully — `search.py` catches the exception and returns a fallback string so the app doesn't crash; historic ChromaDB facts still ground the quiz |
| Keys accidentally pushed to GitHub | OpenAI auto-revokes leaked keys. Rotate immediately in the OpenAI dashboard. Confirm `.env` is listed in `.gitignore` (it already is here) |

---

## 8. Using Gemini instead of OpenAI (optional swap)

If your assignment allows Google Gemini instead of OpenAI:

```bash
pip install google-genai
```

Then in `src/generator.py`, replace the `OpenAI` client block with the
`google-genai` client and its `generate_content` call, keeping the same
`system_instruction` + `user_prompt` structure. The RAG logic
(`database.py`, `search.py`) stays identical — only the final LLM call changes.

---

## 9. How to submit this assignment

1. **Clean up before submitting**:
   - Make sure `.env` (with your real key) is **NOT** included in what you submit/push — only `.env.example`.
   - Delete `venv/` and `chroma_db/` before zipping/pushing (they're regenerated automatically and bloat the submission).
2. **If submitting via Git/GitHub**:
   ```bash
   git init
   git add .
   git commit -m "AI-powered sports quiz RAG agent"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```
   Double-check on GitHub that `.env` does **not** appear in the repo.
3. **If submitting as a zip file**:
   - Zip the whole `sports-quiz-agent/` folder *after* deleting `venv/` and `chroma_db/`.
   - Include a short note/screenshot of the running app in your submission if requested.
4. **Include in your submission**:
   - The source code (all files above).
   - This `README.md` (serves as your write-up/documentation).
   - A screenshot or short screen recording of the app generating a quiz (many graders want visual proof it runs).
