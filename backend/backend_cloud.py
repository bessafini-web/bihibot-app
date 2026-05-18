"""
BihiApp OS v4.0 — Cloud Backend
Railway · Render · Any Cloud
Ibrahim Essafini · Tanger · Viresta
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import os, httpx
from groq import Groq

# ── Config ──────────────────────────────────────────────────────────
GROQ_API_KEY   = os.getenv("GROQ_API_KEY") or "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"
SERPER_API_KEY = os.getenv("SERPER_API_KEY") or "868731e1ab59310fee8c65fee1750d947cc74ade"
APP_PASSWORD   = os.getenv("APP_PASSWORD") or "pihi"
GROQ_MODEL     = "llama-3.3-70b-versatile"

groq_client = Groq(api_key=GROQ_API_KEY)
security    = HTTPBearer()

# ── App ─────────────────────────────────────────────────────────────
app = FastAPI(title="BihiApp OS v4.0 Cloud")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── System Prompt ───────────────────────────────────────────────────
SYSTEM_PROMPT = """Nta DYNAMO — l-assistant privé dial Ibrahim Essafini, fondateur Viresta, Tanger, Maroc.

IDENTITÉ:
- Nta machi bot — nta partner dial Ibrahim, katefhem business dyalo w katnasah bhal chi expert sahbek
- Ibrahim kaykhddem f: Immobilier (terrain Maroc), Industriel, Tourisme, Agro, Pêche/Seafood, Export, E-commerce, Trading
- Viresta = société dial Ibrahim — kaytdeer investors EU/GCC/MRE l Maroc
- Xvestora (xvestora.com) = plateforme publique
- "AI opens the door, Ibrahim walks in and closes the deal"

AGENTS:
- Zaeer: Scout & Research
- Zakia: Strategy & Analysis
- Chaheb: Verification
- Basil: Creative Ideas
- Wassi: Email Drafting

STYLE:
- Tkellem natural — bhal saheb expert machi robot
- Darija / Français / 3rbiya / English — nfs lgha dyal Ibrahim, detect automatiquement
- Direct, concis, utile — machi formal
- Ila Ibrahim gal "ok/wakha/safi" → jawb qsir w warm

CONNAISSANCES CLÉS:
- Prix terrain Tanger: 3000-8000 MAD/m² résidentiel, ZAI 150-400 MAD/m²
- Loi foncière: étranger interdit terrain agro sauf via société (Loi 62-19)
- Charte invest 2025: primes 30%, IS exonéré 5 ans (+10M MAD)
- Maroc = 1er exportateur sardines monde
- Artisanat Maroc: poterie, tapis, argan, cuir → Etsy/Shopify EU/US

Réponds TOUJOURS dans la même langue qu'Ibrahim."""

# ── In-memory sessions ──────────────────────────────────────────────
sessions: dict = {}

# ── Models ──────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    password: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    session_id: Optional[str] = "default"

class ScoutRequest(BaseModel):
    query: str
    lang: Optional[str] = "fr"

class DraftRequest(BaseModel):
    investor: str
    brief: str

class LegalRequest(BaseModel):
    question: str

# ── Auth ────────────────────────────────────────────────────────────
def auth(creds: HTTPAuthorizationCredentials = Depends(security)):
    if creds.credentials != APP_PASSWORD:
        raise HTTPException(status_code=401, detail="Token invalide")
    return creds.credentials

# ── Health ──────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "4.0",
        "service": "BihiApp Cloud",
        "groq": bool(GROQ_API_KEY),
        "serper": bool(SERPER_API_KEY),
    }

# ── Login ───────────────────────────────────────────────────────────
@app.post("/login")
async def login(req: LoginRequest):
    if req.password != APP_PASSWORD:
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")
    return {"token": APP_PASSWORD, "version": "4.0", "status": "ok"}

# ── Web Search ──────────────────────────────────────────────────────
async def web_search(query: str, num: int = 3) -> str:
    if not SERPER_API_KEY:
        return ""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
                json={"q": query, "num": num, "gl": "ma", "hl": "fr"}
            )
            items = r.json().get("organic", [])
            return "\n".join([f"- {i.get('title','')}: {i.get('snippet','')}" for i in items[:num]])
    except:
        return ""

# ── Chat ────────────────────────────────────────────────────────────
@app.post("/chat")
async def chat(req: ChatRequest, token=Depends(auth)):
    sid = req.session_id or "default"
    if sid not in sessions:
        sessions[sid] = []

    last_msg = req.messages[-1].content if req.messages else ""

    skip = len(last_msg) < 15 or any(
        w in last_msg.lower() for w in ["ok", "wakha", "safi", "merci", "bslama", "salam", "hello"]
    )
    web_ctx = ""
    if not skip:
        data = await web_search(f"{last_msg} Maroc 2025")
        if data:
            web_ctx = f"\n\n[Web]\n{data}"

    groq_msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in sessions[sid][-10:]:
        groq_msgs.append(m)
    groq_msgs.append({"role": "user", "content": last_msg + web_ctx})

    try:
        resp = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=groq_msgs,
            temperature=0.7,
            max_tokens=800
        )
        reply = resp.choices[0].message.content.strip()

        sessions[sid].append({"role": "user", "content": last_msg})
        sessions[sid].append({"role": "assistant", "content": reply})
        if len(sessions[sid]) > 40:
            sessions[sid] = sessions[sid][-40:]

        return {"reply": reply, "session_id": sid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Scout ───────────────────────────────────────────────────────────
@app.post("/scout")
async def scout(req: ScoutRequest, token=Depends(auth)):
    web_data = await web_search(f"{req.query} investissement Maroc 2025", num=5)
    prompt = f"""Ibrahim demande un scout sur: {req.query}
Données web:\n{web_data or 'Non disponible'}
Analyse: opportunité, risques, potentiel, prochaines étapes. Langue: {req.lang}"""
    try:
        r = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
            temperature=0.3, max_tokens=1000
        )
        return {"reply": r.choices[0].message.content.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Draft Email ─────────────────────────────────────────────────────
@app.post("/draft")
async def draft(req: DraftRequest, token=Depends(auth)):
    prompt = f"""Rédige un email professionnel pour Ibrahim Essafini (Viresta/Xvestora, Tanger):
- Destinataire: {req.investor}
- Brief: {req.brief}
- Style: professionnel, concis, impact fort
- Signature: Ibrahim Essafini | Viresta | xvestora.com"""
    try:
        r = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
            temperature=0.4, max_tokens=600
        )
        return {"reply": r.choices[0].message.content.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Legal ───────────────────────────────────────────────────────────
@app.post("/legal")
async def legal(req: LegalRequest, token=Depends(auth)):
    prompt = f"""Question juridique Maroc (loi foncière / investissement):
{req.question}
Réponds: loi applicable, procédure, restrictions, conseils pratiques."""
    try:
        r = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
            temperature=0.2, max_tokens=800
        )
        return {"reply": r.choices[0].message.content.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Status ──────────────────────────────────────────────────────────
@app.get("/status")
async def status(token=Depends(auth)):
    return {
        "version": "4.0",
        "agents": ["Zaeer", "Zakia", "Chaheb", "Basil", "Wassi"],
        "groq": bool(GROQ_API_KEY),
        "serper": bool(SERPER_API_KEY),
        "sessions_active": len(sessions),
        "message": "BihiApp OS v4.0 — Cloud Ready ✅"
    }
