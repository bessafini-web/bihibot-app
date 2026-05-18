"""agents/basil.py — Basil V4 — Creative + Wild Card Protocol"""
import json
from ai.ai_router import route_ai
from sheets.execution_log import log

SYSTEM_PROMPT = """You are Basil, the Creative agent of BihiApp OS.
Generate bold, unconventional ideas. Think outside the box. Focus on Morocco/Maghreb.
For EVERY task provide: Classic Solution + Bold Wild Card.
Output ONLY valid JSON:
- classic_solution (string)
- bold_idea (string)
- scenario (string)
- risk_level (Low/Medium/High)
- potential_return (string)
- recommendation (Try/Study/Later)
- creative_score (0-100)
No markdown. ONLY JSON."""

def generate_idea(opportunity):
    prompt = f"""Generate creative angles for this opportunity (BihiApp OS/Morocco):
{json.dumps(opportunity, indent=2, ensure_ascii=False)}
Think unconventional — what would a bold entrepreneur do? Morocco/Maghreb context, BihiApp OS brand."""
    raw = route_ai("creative", SYSTEM_PROMPT, prompt, max_tokens=700)
    raw = raw.replace("```json","").replace("```","").strip()
    try:
        data = json.loads(raw)
    except:
        data = {"classic_solution":"Standard approach.","bold_idea":"Manual creative review.",
                "scenario":"","risk_level":"Medium","potential_return":"Unknown",
                "recommendation":"Study","creative_score":0}
    log("Basil","generate_idea","BihiApp",f"Creative: {opportunity.get('title','')}","Auto","Done",False)
    return data
