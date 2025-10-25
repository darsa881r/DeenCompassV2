# DeenCompassV2 — Citations-First Scholar Chat

DeenCompass is a lightweight web + API app that helps users going through tough times ask faith-aligned questions and receive **citations-first** answers grounded in **Qur’an, authentic ḥadīth (with grading), fiqh across madhāhib, and reputable tafsīr**.  
**Educational only — not a fatwā engine.**


```md
<p align="center">
  <img src="Screenshot 2025-10-25 015203.png" alt="DeenCompass demo UI" width="820">
</p>

---

## ✨ Features

- **Citations-first** responses (no speculation; sources required).
- **Simple UI**: one question box → “Ask the Scholar” → answer.
- **Pluggable providers** (server-side):
  - `openai` (default; e.g., `gpt-5`, `gpt-4o-mini`)
  - `gemini` (Google GenAI)
  - `llama` (OpenAI-compatible local server)
- **FastAPI** backend with clean JSON responses.
- **No secrets in frontend** — API keys live in `.env` on the server.

---

## 🏗️ Project Structure

```
DeenCompassV2/
├─ server/
│  ├─ main.py                  # /health, /chat (/api/chat) endpoints
│  ├─ requirements.txt
│  ├─ .env.example
│  └─ providers/
│     ├─ base.py
│     ├─ openai_provider.py
│     ├─ gemini_provider.py
│     └─ llama_provider.py
├─ web/
│  ├─ index.html               # Question box + "Ask the Scholar"
│  └─ app.js                   # Calls server and renders answer
└─ .gitignore
```

---

## 🚀 Quick Start

> Uses **conda-forge** for most packages and **pip** for Google’s new GenAI SDK (optional).  
> If you’re only using OpenAI, you can skip the `pip install google-genai` step.

### 1) Create & activate environment

```bash
conda create -n deencompass -c conda-forge python=3.11 -y
conda activate deencompass

# Server deps from conda-forge
conda install -c conda-forge fastapi pydantic python-dotenv uvicorn httpx groq -y

# (Optional) Gemini new SDK (not on conda-forge yet)
pip install google-genai
```

### 2) Configure secrets

Copy `server/.env.example` → `server/.env` and fill in:

```ini
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
LLAMA_BASE_URL=http://127.0.0.1:1234/v1
```

> Ensure `.env` is **git-ignored** (it is in this repo’s `.gitignore`).

### 3) Run the API server

```bash
cd server
uvicorn main:app --reload --port 8000
# Docs: http://127.0.0.1:8000/docs
```

> The app typically accepts `POST /api/chat`. Some setups also expose `POST /chat`. Check the docs and adjust the frontend endpoint if needed.

### 4) Open the web app

- Open `web/index.html` in your browser (double-click or serve locally).
- Type a question → **Ask the Scholar** → view the answer with citations.

---

## 🔌 API

### `POST /api/chat`  *(or `/chat` depending on your router prefix)*

**Request body (OpenAI-compatible messages):**
```json
{
  "provider": "openai",
  "model": "gpt-5",
  "messages": [
    { "role": "system", "content": "Citations-first instructions..." },
    { "role": "user",   "content": "Your question..." }
  ]
}
```

**Normalized response (recommended):**
```json
{
  "content": "Answer text here with citations...",
  "raw": { "providerSpecificResponse": "..." }
}
```

**Legacy minimal response (also supported by the frontend):**
```json
{ "text": "Answer text here..." }
```

---

## 🖥️ Frontend (web)

- Static HTML/JS (no build step, no secrets).
- Default endpoint in `web/app.js` is `http://127.0.0.1:8000/api/chat` — change if your server only exposes `/chat`.
- Sends a strong **system** instruction enforcing **citations-first, no fatwā**, then your **user** question.
- Displays clean text using a small, robust extractor (avoids raw JSON dumps).

---

## 🔐 Security & Privacy

- **Never commit secrets**. Keep keys only in `server/.env`.
- GitHub may block pushes if a secret is detected (GH013). If that happens:
  1. **Rotate** the exposed key immediately (create a new one).
  2. **Remove** the key from files and **rewrite history** (e.g., `git filter-repo` or BFG).
  3. **Force-push** with `--force-with-lease`.
- UI reminder: share **minimal PII**; this app is **educational only**.

Suggested `.gitignore` entries (already included):

```
.env
.venv/
venv/
__pycache__/
node_modules/
.api
test.py
*_backup*.py
*_backup*.js
```

---

## 🧰 Troubleshooting

**404 on `/chat` vs `/api/chat`**  
- Open `http://127.0.0.1:8000/docs` to confirm the exact path.
- Update the frontend endpoint in `web/app.js` accordingly.

**CORS passes but POST fails**  
- Ensure FastAPI has permissive CORS during development:
  ```python
  from fastapi.middleware.cors import CORSMiddleware
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],   # tighten in production
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

**Frontend shows JSON instead of text**  
- Your server may be returning `{ text: ... }`, `{ content: ... }`, or provider-raw.  
  The frontend’s extractor handles common shapes; or normalize server responses to `{ "content": "...", "raw": {...} }`.

**Git push blocked (GH013)**  
- Rotate key → scrub files/history → push again. See GitHub “Push protection” docs.

---

## 🗺️ Roadmap

- ✅ Minimal Q → A flow (citations-first)
- 🔜 Streaming responses (type-as-they-arrive)
- 🔜 Reasoning/effort toggle & max output token control
- 🔜 Per-madhhab summaries with footnotes
- 🔜 Copy-to-clipboard & export to PDF
- 🔜 Optional RAG over a vetted corpus

---

## 🤝 Contributing

PRs and suggestions welcome!  
Please preserve the educational, **citations-first** philosophy and never introduce secrets into the repo or CI.

---

## 📄 License

Copyright © 2025.

- If open-sourcing: add an OSI license (e.g., MIT) to `LICENSE`.
- Otherwise: “All rights reserved.”

---

**Support / Issues:**  
Open an issue on GitHub with your environment (OS, Python version), steps to reproduce, and relevant logs (with secrets redacted).
