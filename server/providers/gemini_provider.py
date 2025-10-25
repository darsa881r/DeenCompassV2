import os
from google import genai
from google.genai import types

GEMINI_MODEL_ID = os.getenv("GEMINI_MODEL_ID", "gemini-2.5-flash")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_reply(messages, system_prompt, gen):
    """
    Gemini likes a "conversation transcript" string; this keeps it simple.
    We'll pass our system instruction via 'system_instruction' and the
    generation controls via GenerateContentConfig.
    """
    # Convert messages list to "role: text" lines
    convo = "\n".join(f"{m.get('role','user')}: {m.get('content','')}" for m in messages)

    temperature = float(gen.get("temperature", 0.2))
    top_p       = float(gen.get("top_p", 0.9))
    top_k       = int(gen.get("top_k", 40))
    max_tokens  = int(gen.get("max_tokens", 700))

    cfg = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        max_output_tokens=max_tokens
    )
    r = client.models.generate_content(model=GEMINI_MODEL_ID, contents=convo, config=cfg)
    return (r.text or "").strip()
