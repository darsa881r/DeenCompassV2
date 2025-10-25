"""
base.py
-------
Defines the one function every provider module must implement.
This keeps main.py simple and replaceable later.
"""

from typing import List, Dict

def generate_reply(messages: List[Dict], system_prompt: str, gen: Dict) -> str:
    """
    Parameters
    ----------
    messages : list of {role:str, content:str}
        Example: [{"role": "user", "content": "Assalamu alaikum"}]
        (In future you can add previous turns to preserve chat history.)
    system_prompt : str
        The policy/instructions the model should ALWAYS follow.
    gen : dict
        Generation controls (temperature, top_p, max_tokens, etc.)
        We load these from .env so beginners can tune *without* touching code.

    Returns
    -------
    str
        Plain text answer from the model.
    """
    raise NotImplementedError("Each provider must implement generate_reply()")
