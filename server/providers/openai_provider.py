"""
openai_provider.py  (GPT-5 reasoning-only)
------------------------------------------
Tiny wrapper around the OpenAI *Responses API* for reasoning models
like GPT-5. We intentionally DO NOT send sampling controls such as
`temperature` or `top_p` because reasoning models reject them.

Reads optional extras from environment variables:
- OPENAI_API_KEY                (required)
- OPENAI_MODEL_ID               (defaults to "gpt-5")
- OPENAI_SERVICE_TIER           (auto|default|flex|priority)
- OPENAI_TRUNCATION             (disabled|auto)
- OPENAI_STORE                  (true|false)
- OPENAI_PARALLEL_TOOL_CALLS    (true|false)
- OPENAI_BACKGROUND             (true|false)
- REASONING_EFFORT              (low|medium|high)
- REASONING_BUDGET_TOKENS       (integer)

Returns aggregated text via `resp.output_text`.
"""

import os
from typing import Optional
from openai import OpenAI

# --- client & model ---
OPENAI_MODEL_ID = os.getenv("OPENAI_MODEL_ID", "gpt-5")
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    # These two are optional; omit if you don't use org/project routing.
    organization=os.getenv("OPENAI_ORGANIZATION_ID") or None,
    project=os.getenv("OPENAI_PROJECT_ID") or None,
)

# --- helpers to read env safely ---
def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")

def _env_str(name: str) -> Optional[str]:
    raw = os.getenv(name)
    if not raw:
        return None
    s = raw.strip()
    return s if s else None

def _env_int(name: str) -> Optional[int]:
    raw = os.getenv(name)
    if not raw:
        return None
    s = raw.strip()
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        print(f"[env] WARN: {name} expected int, got {raw!r}; ignoring")
        return None

def _format(messages, system_prompt):
    """
    Prepend your system instruction so the model always sees your rules first.
    The Responses API accepts role-based messages in `input`.
    """
    return [{"role": "system", "content": system_prompt}, *messages]


def generate_reply(messages, system_prompt, _gen=None) -> str:
    """
    Make a single non-streaming call to the Responses API using GPT-5.
    Only sends fields reasoning models accept.
    """
    # Hard cap for visible output (and reasoning) tokens.
    # You can control this from .env via GEN_MAX_TOKENS (read by main.py),
    # but we read it again here so the provider works standalone, too.
    max_tokens = _env_int("GEN_MAX_TOKENS") or 5000

    # Optional Responses-API extras (only added if present).
    extras = {}

    st = _env_str("OPENAI_SERVICE_TIER")      # auto|default|flex|priority
    if st:
        extras["service_tier"] = st

    trunc = _env_str("OPENAI_TRUNCATION")     # disabled|auto
    if trunc:
        extras["truncation"] = trunc

    if os.getenv("OPENAI_STORE") is not None:
        extras["store"] = _env_bool("OPENAI_STORE", True)

    if os.getenv("OPENAI_PARALLEL_TOOL_CALLS") is not None:
        extras["parallel_tool_calls"] = _env_bool("OPENAI_PARALLEL_TOOL_CALLS", True)

    if os.getenv("OPENAI_BACKGROUND") is not None:
        extras["background"] = _env_bool("OPENAI_BACKGROUND", False)

    # Reasoning block (applies to GPT-5 / o-series)
    reasoning = {}
    effort = _env_str("REASONING_EFFORT")     # low|medium|high
    if effort:
        reasoning["effort"] = effort
    budget = _env_int("REASONING_BUDGET_TOKENS")
    if budget is not None:
        reasoning["budget_tokens"] = budget
    if reasoning:
        extras["reasoning"] = reasoning

    # Build the request — note: NO temperature, NO top_p, NO stop here.
    resp = client.responses.create(
        model=OPENAI_MODEL_ID,
        input=_format(messages, system_prompt),
        max_output_tokens=max_tokens,
        **extras
    )

    # Helpful debug
    req_id = getattr(resp, "request_id", None) or getattr(resp, "id", None)
    used_tier = getattr(resp, "service_tier", None)
    print(
        f"[openai:gpt-5] request_id={req_id} service_tier={used_tier} "
        f"max_output_tokens={max_tokens}"
    )

    return resp.output_text or ""
