from google import genai
from google.genai import types
from flask import current_app
import logging, os

def analyze_with_gemini(prompt: str) -> str:
    """Kirim prompt ke Gemini API dan ambil hasil teksnya."""
    try:
        api_key = current_app.config.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "API Key Gemini belum diset di environment."

        os.environ["GEMINI_API_KEY"] = api_key  # pastikan tersedia untuk library

        client = genai.Client()
        resp = client.models.generate_content(
            model=current_app.config.get("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_budget=current_app.config.get("GEMINI_THINKING_BUDGET", 0)
                )
            ),
        )
        return resp.text.strip() if resp and resp.text else "Tidak ada hasil dari Gemini."
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        return f"Gagal menganalisis dengan Gemini: {e}"