import os
from groq import Groq

LLAMA_MODEL_ID = os.getenv("LLAMA_MODEL_ID", "REPLACE_WITH_LLAMA_MODEL_ID")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_reply(messages, system_prompt, gen):
    """
    Groq exposes a Chat Completions API for Llama models.
    We pass the same tuning controls (mapped to Chat Completions names).
    """
    temperature = float(gen.get("temperature", 0.2))
    top_p       = float(gen.get("top_p", 0.9))
    max_tokens  = int(gen.get("max_tokens", 700))

    # Build standard Chat Completions messages (system → user/assistant)
    msg = [{"role": "system", "content": system_prompt}, *messages]

    r = client.chat.completions.create(
        model=LLAMA_MODEL_ID,
        messages=msg,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
    )
    # Return first choice text safely
    return (r.choices[0].message.content if r and r.choices else "") or ""
