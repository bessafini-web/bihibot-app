"""
BihiApp OS v5.0
config.py — Configuration centrale
"""
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN        = os.getenv("TELEGRAM_TOKEN")
IBRAHIM_CHAT_ID       = os.getenv("IBRAHIM_CHAT_ID")
GROQ_API_KEY          = os.getenv("GROQ_API_KEY")
GROQ_MODEL            = "llama-3.3-70b-versatile"
GEMINI_API_KEY        = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL          = "gemini-2.0-flash"
OPENAI_API_KEY        = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL          = "gpt-4o-mini"
SERPER_API_KEY        = os.getenv("SERPER_API_KEY")
APIFY_TOKEN           = os.getenv("APIFY_TOKEN", "")
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
GOOGLE_SHEET_ID         = os.getenv("GOOGLE_SHEET_ID")
SPREADSHEET_NAME        = os.getenv("SPREADSHEET_NAME", "BihiApp_DB")
APP_PASSWORD            = os.getenv("APP_PASSWORD", "pihi")
FINANCIAL_PASSWORD_HASH = os.getenv("FINANCIAL_PASSWORD_HASH", "")
RESEND_API_KEY          = os.getenv("RESEND_API_KEY", "")
TRUST_SCORE_MIN       = 50
RISK_SCORE_MAX        = 70
CONFIDENCE_MIN        = 60
CONFIDENCE_AUTO_FETCH = 60
CACHE_DIR = ".cache"
CACHE_DURATION = {
    "real_estate": 12*3600, "industriel": 12*3600, "tourisme": 24*3600,
    "agro": 24*3600, "export": 24*3600, "ecommerce": 2*3600,
    "trading": 1*3600, "crypto": 30*60, "legal": 30*24*3600,
    "social": 2*3600, "default": 6*3600,
}
AI_ROUTING = {
    "scout":"groq","verify":"groq","analyze":"groq","research":"gemini",
    "legal":"gemini","email":"gpt4o_mini","dossier":"gpt4o_mini",
    "creative":"groq","weekly":"groq","social":"groq","intent":"groq",
}
# ── Dynamo Memory — load at startup ─────────────────────────────────
def load_dynamo_memory():
    try:
        base = os.path.dirname(os.path.abspath(__file__))
        # Load operator memory
        mem1 = open(os.path.join(base, "DYNAMO_MEMORY.md"), encoding="utf-8").read()
        # Load project state
        proj_path = os.path.join(base, "BIHIAPP_14MAI2026_v2.md")
        mem2 = open(proj_path, encoding="utf-8").read() if os.path.exists(proj_path) else ""
        # Combine — memory first, then project state summary
        combined = mem1
        if mem2:
            # Extract only the key sections to keep prompt lean
            lines = mem2.split('\n')
            relevant = [l for l in lines if any(k in l for k in
                ['✅','❌','🚀','📌','##','PRIORIT','ACCOMPLI','RESTANT','PROCHAINE'])]
            combined += f"\n\n## PROJECT STATE\n" + "\n".join(relevant[:40])
        return combined
    except: return ""

DYNAMO_MEMORY = load_dynamo_memory()
ALWAYS_ON_AGENTS  = ["dynamo","zaeer","zakia"]
ON_DEMAND_AGENTS  = ["chaheb","basil","wassi"]
SECTORS = ["Real Estate","Industriel","Tourisme","Agro","Export","E-Commerce","Trading"]
PHASE1_PRIMARY   = ["E-Commerce","Export"]
PHASE1_SECONDARY = ["Real Estate","Agro"]
PHASE1_LATER     = ["Trading","Industriel","Tourisme"]
DEFAULT_SOURCES = {
    "Real Estate":["mubawab.ma","sarouty.ma","avito.ma","amdie.ma","cri-invest.ma"],
    "Export":["trademap.org","cnce.org.ma","amdie.ma","alibaba.com"],
    "Agro":["onssa.gov.ma","agriculture.gov.ma","trademap.org"],
    "Industriel":["amdie.ma","cfcim.org","zai.ma"],
    "Tourisme":["onmt.ma","airbnb.com","booking.com"],
    "E-Commerce":["aliexpress.com","1688.com","tiktok.com/shop","amazon.com/movers"],
    "Trading":["coingecko.com","tradingview.com","reuters.com"],
    "Legal":["sgg.gov.ma","amdie.ma","ammc.ma","bkam.ma","eur-lex.europa.eu"],
}
