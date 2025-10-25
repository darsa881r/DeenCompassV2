"""
main.py  (GPT-5 reasoning-only)
--------------------------------
FastAPI server that exposes a minimal chat endpoint for GPT-5.

Endpoints:
- GET  /health         quick JSON health check
- POST /api/chat       body: { "messages": [ {role, content}, ... ] } -> { "text": "..." }

Notes for beginners:
- Put your API key and simple knobs in server/.env (never commit keys).
- This app does *not* send temperature/top_p, because GPT-5 rejects them.
- You can still control output length via GEN_MAX_TOKENS and add reasoning
  effort/budget via REASONING_EFFORT / REASONING_BUDGET_TOKENS.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# 1) Load server/.env (API key, model id, and any optional flags)
load_dotenv()

# 2) Import our GPT-5 provider (no provider switch — this app is GPT-5 only)
from providers import openai_provider as llm  # noqa: E402

# 3) (Optional) read a few env values for /health, so you can see what's active
def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")

def _env_str(name: str, default: str = "") -> str:
    raw = os.getenv(name)
    if not raw:
        return default
    s = raw.strip()
    return s if s else default

def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if not raw or not raw.strip():
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default

ACTIVE_CONFIG = {
    "model": _env_str("OPENAI_MODEL_ID", "gpt-5"),
    "max_output_tokens": _env_int("GEN_MAX_TOKENS", 5000),
    "reasoning_effort": _env_str("REASONING_EFFORT", "medium"),
    "reasoning_budget_tokens": _env_int("REASONING_BUDGET_TOKENS", 1000),
    "service_tier": _env_str("OPENAI_SERVICE_TIER", "auto"),
    "truncation": _env_str("OPENAI_TRUNCATION", "disabled"),
    "store": _env_bool("OPENAI_STORE", True),
    "parallel_tool_calls": _env_bool("OPENAI_PARALLEL_TOOL_CALLS", True),
    "background": _env_bool("OPENAI_BACKGROUND", False),
}

# 4) Your system instruction (policy). Edit the wording as you like.
SYSTEM_PROMPT = (
  "You are DeenCompass MVP. Only answer with Qur’an, hadith (with grading), "
  "sīrah, tafseer or fiqh citations that are verifiable. If not confident, briefly say "
  "you can’t answer with sources, suggest asking a qualified scholar, and "
  "optionally point to trusted references. No hallucinations."
)

# 5) FastAPI app + permissive CORS for local development
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ok for local dev; restrict to your domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# 6) Request model for /api/chat
class ChatBody(BaseModel):
    # Minimal shape expected by openai_provider.generate_reply()
    messages: list  # e.g., [{"role": "user", "content": "Assalamu alaikum"}]

@app.get("/health")
def health():
    """
    Open in your browser to confirm everything is wired:
    http://127.0.0.1:8000/health
    """
    return {"status": "ok", "provider": "openai-gpt5-reasoning", "config": ACTIVE_CONFIG}

@app.post("/api/chat")
def chat(body: ChatBody):
    """
    Your web page calls this endpoint with a list of messages.
    We prepend SYSTEM_PROMPT inside the provider; it returns plain text.
    """
    text = llm.generate_reply(body.messages, SYSTEM_PROMPT, None)
    return {"text": text}
