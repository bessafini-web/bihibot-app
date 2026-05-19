"""
BihiApp OS v5.0 — Backend API
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os, tempfile, httpx

# ── Paths ──────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

# ── Load modules ───────────────────────────────────────────────────
try:
    from dynamo.dynamo import dynamo
    from core.lang import detect
    DYNAMO_OK = True; DYNAMO_ERR = ""
except Exception as e:
    DYNAMO_OK = False; DYNAMO_ERR = str(e)

try:
    from db import get_all_records
    from sheets.investors import get_active_investors
    from sheets.opportunities import get_all_opportunities, get_by_sector
    from sheets.alerts import get_pending_alerts
    from memory.ilm import get_active_rules
    from memory.weekly import generate_weekly
    SHEETS_OK = True; SHEETS_ERR = ""
except Exception as e:
    SHEETS_OK = False; SHEETS_ERR = str(e)

APP_PASSWORD = "pihi"

# ── App ────────────────────────────────────────────────────────────
app = FastAPI(title="BihiApp OS v4.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
security = HTTPBearer()

# ── Serve frontend ─────────────────────────────────────────────────
@app.get("/")
async def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

if os.path.exists(FRONTEND_DIR):
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

# ── Models ─────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    password: str

class ChatRequest(BaseModel):
    messages: List[dict]
    action: Optional[str] = None

class ScoutRequest(BaseModel):
    query: str
    sector: Optional[str] = "Real Estate"
    lang: Optional[str] = "french"

class DraftRequest(BaseModel):
    investor: str
    brief: str
    sector: Optional[str] = "Real Estate"
    lang: Optional[str] = "french"

class LegalRequest(BaseModel):
    question: str
    sector: Optional[str] = "real_estate"
    lang: Optional[str] = "french"

class FeedbackRequest(BaseModel):
    command: str
    context: str
    correction: str

def auth(creds: HTTPAuthorizationCredentials = Depends(security)):
    return creds.credentials

# ── Auth ───────────────────────────────────────────────────────────
@app.post("/login")
async def login(req: LoginRequest):
    if req.password != APP_PASSWORD:
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")
    return {"token": APP_PASSWORD, "version": "4.0", "dynamo": DYNAMO_OK, "sheets": SHEETS_OK}

# ── Health ─────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {
        "status": "ok", "version": "4.0",
        "dynamo": DYNAMO_OK, "sheets": SHEETS_OK,
        "dynamo_error": DYNAMO_ERR or None,
        "sheets_error": SHEETS_ERR or None,
    }

# ── Chat ───────────────────────────────────────────────────────────
@app.post("/chat")
async def chat(req: ChatRequest, token=Depends(auth)):
    if not DYNAMO_OK:
        raise HTTPException(status_code=503, detail=f"Dynamo unavailable: {DYNAMO_ERR}")
    last = req.messages[-1]["content"] if req.messages else ""
    try:
        lang = detect(last)
        payload = {"lang": lang}
        if req.action:
            payload["action"] = req.action
        result = dynamo.receive(last, payload)
        return {"reply": result, "lang": lang}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Scout ──────────────────────────────────────────────────────────
@app.post("/scout")
async def scout(req: ScoutRequest, token=Depends(auth)):
    if not DYNAMO_OK:
        raise HTTPException(status_code=503, detail="Dynamo unavailable")
    try:
        result = dynamo.receive(req.query or "scout", {
            "lang": req.lang, "sector": req.sector, "query": req.query
        })
        return {"reply": result, "sector": req.sector}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Draft ──────────────────────────────────────────────────────────
@app.post("/draft")
async def draft(req: DraftRequest, token=Depends(auth)):
    if not DYNAMO_OK:
        raise HTTPException(status_code=503, detail="Dynamo unavailable")
    try:
        result = dynamo.receive(f"draft email {req.investor} {req.brief}", {
            "lang": req.lang, "investor": req.investor, "sector": req.sector
        })
        return {"reply": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Legal ──────────────────────────────────────────────────────────
@app.post("/legal")
async def legal(req: LegalRequest, token=Depends(auth)):
    if not DYNAMO_OK:
        raise HTTPException(status_code=503, detail="Dynamo unavailable")
    try:
        result = dynamo.receive(f"legal {req.question}", {
            "lang": req.lang, "sector": req.sector
        })
        return {"reply": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Weekly ─────────────────────────────────────────────────────────
@app.get("/weekly")
async def weekly(lang: str = "french", token=Depends(auth)):
    try:
        result = generate_weekly(lang) if SHEETS_OK else dynamo.receive("weekly", {"lang": lang})
        return {"reply": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Feedback ───────────────────────────────────────────────────────
@app.post("/feedback")
async def feedback(req: FeedbackRequest, token=Depends(auth)):
    if not DYNAMO_OK:
        raise HTTPException(status_code=503, detail="Dynamo unavailable")
    try:
        result = dynamo.correct(req.command, req.context, req.correction)
        return {"reply": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Shield ─────────────────────────────────────────────────────────
@app.get("/shield")
async def shield(token=Depends(auth)):
    result = dynamo.receive("shield_status", {})
    return {"reply": result}

@app.post("/shield/{action}")
async def shield_action(action: str, token=Depends(auth)):
    a = {"on": "shield_activate", "off": "shield_resume"}.get(action, "shield_status")
    result = dynamo.receive(a, {})
    return {"reply": result}

# ── Data — 19 Sheets ───────────────────────────────────────────────
@app.get("/data/summary")
async def summary(token=Depends(auth)):
    if not SHEETS_OK:
        return {"sheets": False, "dynamo": DYNAMO_OK}
    try:
        investors  = get_active_investors()
        ops        = get_all_opportunities()
        alerts     = get_pending_alerts()
        rules      = get_active_rules()
        return {
            "sheets": True, "dynamo": DYNAMO_OK,
            "investors_active":   len(investors),
            "opportunities_total": len(ops),
            "opportunities_high": len([o for o in ops if o.get("Priority") == "High"]),
            "opportunities_new":  len([o for o in ops if o.get("Status") == "New"]),
            "alerts_pending":     len(alerts),
            "ilm_rules":          len(rules),
        }
    except Exception as e:
        return {"sheets": False, "error": str(e)}

@app.get("/data/investors")
async def investors(token=Depends(auth)):
    if not SHEETS_OK: raise HTTPException(503)
    return {"investors": get_active_investors()}

@app.get("/data/opportunities")
async def opportunities(sector: str = None, token=Depends(auth)):
    if not SHEETS_OK: raise HTTPException(503)
    data = get_by_sector(sector) if sector else get_all_opportunities()
    return {"count": len(data), "opportunities": data}

@app.get("/data/alerts")
async def alerts(token=Depends(auth)):
    if not SHEETS_OK: raise HTTPException(503)
    return {"alerts": get_pending_alerts()}

@app.get("/data/leads/{sector}")
async def leads(sector: str, token=Depends(auth)):
    if not SHEETS_OK: raise HTTPException(503)
    sheet_map = {
        "industriel": "LEADS_INDUSTRIEL",
        "tourisme":   "LEADS_TOURISME",
        "agro":       "LEADS_AGRO",
        "export":     "EXPORT_MATCHES",
        "ecommerce":  "ECOMMERCE_OPS",
    }
    sheet = sheet_map.get(sector.lower())
    if not sheet: raise HTTPException(404, f"Sector {sector} not found")
    try:
        data = get_all_records(sheet)
        return {"sector": sector, "count": len(data), "data": data}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/data/ilm")
async def ilm(token=Depends(auth)):
    if not SHEETS_OK: raise HTTPException(503)
    return {"rules": get_active_rules()}


# ── Whisper Transcription — Groq ───────────────────────────────────
@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...), lang: str = "ar", token=Depends(auth)):
    GROQ_KEY = os.getenv("GROQ_API_KEY", "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")
    try:
        audio_bytes = await audio.read()
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name
        async with httpx.AsyncClient(timeout=30) as client:
            with open(tmp_path, "rb") as af:
                r = await client.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {GROQ_KEY}"},
                    files={"file": ("audio.webm", af, "audio/webm")},
                    data={
                        "model": "whisper-large-v3-turbo",
                        "prompt": "BihiApp Viresta Tanger darija trading immobilier export",
                        "response_format": "verbose_json",
                    }
                )
        os.unlink(tmp_path)
        if r.status_code == 200:
            data = r.json()
            text = data.get("text", "").strip()
            detected = data.get("language", lang)
            return {"text": text, "ok": True, "detected_lang": detected}
        else:
            return {"text": "", "ok": False, "error": r.text}
    except Exception as e:
        return {"text": "", "ok": False, "error": str(e)}

# ── Groq Orpheus TTS ───────────────────────────────────────
@app.post("/tts")
async def tts(request: Request, token=Depends(auth)):
    GROQ_KEY = os.getenv("GROQ_API_KEY", "")
    try:
        body = await request.json()
        text = body.get("text", "").strip()[:200]  # Orpheus limit: 200 chars
        lang = body.get("lang", "french").lower()
        if not text:
            return {"ok": False, "error": "No text"}
        # Select model and voice by language
        if lang == "arabic":
            model = "canopylabs/orpheus-arabic-saudi"
            voice = "sultan"
        else:
            model = "canopylabs/orpheus-v1-english"
            voice = "troy"
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                "https://api.groq.com/openai/v1/audio/speech",
                headers={
                    "Authorization": f"Bearer {GROQ_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "voice": voice,
                    "input": text,
                    "response_format": "wav",
                }
            )
        if r.status_code == 200:
            from fastapi.responses import Response
            return Response(content=r.content, media_type="audio/wav")
        else:
            return {"ok": False, "error": r.text}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ── Setup DB ───────────────────────────────────────────────────────
@app.post("/setup")
async def setup_db(token=Depends(auth)):
    try:
        from db import setup_all_sheets
        setup_all_sheets()
        return {"ok": True, "message": "19 sheets created/verified"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Debug sheets ────────────────────────────────────────────────────
@app.get("/debug/sheets")
async def debug_sheets(token=Depends(auth)):
    try:
        from db import _init, _spreadsheet, GOOGLE_SHEET_ID
        _init()
        import db as _db
        sheets = [ws.title for ws in _db._spreadsheet.worksheets()]
        return {"sheet_id": GOOGLE_SHEET_ID, "sheets": sheets, "count": len(sheets)}
    except Exception as e:
        return {"error": str(e)}
