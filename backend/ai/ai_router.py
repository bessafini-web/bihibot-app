"""ai/ai_router.py — Multi-AI Router V4 — Groq / Gemini / GPT-4o-mini"""
import os
from groq import Groq
from google import genai as genai_new
from google.genai import types as genai_types
from config import (GROQ_API_KEY, GROQ_MODEL, GEMINI_API_KEY, GEMINI_MODEL,
                    OPENAI_API_KEY, OPENAI_MODEL, AI_ROUTING)

_groq = Groq(api_key=GROQ_API_KEY)
_gemini = genai_new.Client(api_key=GEMINI_API_KEY)
_openai = None
if OPENAI_API_KEY:
    try:
        from openai import OpenAI
        _openai = OpenAI(api_key=OPENAI_API_KEY)
    except: pass

# Tasks qui méritent température élevée (conversation naturelle)
WARM_TASKS = {"scout", "other", "chat", "free"}

def route_ai(task: str, system: str, prompt: str, max_tokens: int = 800) -> str:
    model_choice = AI_ROUTING.get(task, "groq")
    # Free chat → Groq — kayatbi3 instructions ahsen mn Gemini
    if task in WARM_TASKS:
        model_choice = "groq"
    if model_choice == "gpt4o_mini" and not _openai:
        model_choice = "groq"
    temperature = 0.7 if task in WARM_TASKS else 0.2
    try:
        if model_choice == "gemini":
            response = _gemini.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    system_instruction=system,
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
            return response.text.strip()
        elif model_choice == "groq":
            r = _groq.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role":"system","content":system},{"role":"user","content":prompt}],
                temperature=temperature, max_tokens=max_tokens)
            return r.choices[0].message.content.strip()
        elif model_choice == "gpt4o_mini":
            r = _openai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role":"system","content":system},{"role":"user","content":prompt}],
                temperature=temperature, max_tokens=max_tokens)
            return r.choices[0].message.content.strip()
    except Exception as e:
        try:
            r = _groq.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role":"system","content":system},{"role":"user","content":prompt}],
                temperature=0.7, max_tokens=max_tokens)
            return r.choices[0].message.content.strip()
        except Exception as e2:
            return f"Désolé, problème technique momentané. Réessaie dans quelques secondes."
