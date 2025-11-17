Light wrapper for Google Generative AI (Gemini). Configure with env var GOOGLE_API_KEY.
This module exposes `summarize_analysis(prompt)` which returns a human-friendly string.

import os
from typing import Optional

try:
    import google.generativeai as genai
except Exception:
    genai = None

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if genai and GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


def summarize_analysis(prompt: str, model: str = 'gemini-1.5') -> str:
    """Call Gemini to produce a concise recommendation.
    If Gemini client is not installed or key missing, returns the prompt as a fallback summary indicator.
    """
    if not genai or not GOOGLE_API_KEY:
        return "[Gemini not configured] " + prompt[:1000]
    try:
        response = genai.generate_text(model=model, prompt=prompt, max_output_tokens=512)
        return response.text
    except Exception as e:
        return f"[Gemini call failed] {str(e)}
