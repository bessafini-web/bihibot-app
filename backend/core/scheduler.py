"""core/scheduler.py — Auto-Scouting Background Scheduler"""
import threading, time, logging, asyncio
from config import SCHEDULE_HOURS
logger = logging.getLogger(__name__)
_bot_app = None
_ibrahim_chat_id = None
_running = False

def init(bot_app, ibrahim_chat_id):
    global _bot_app, _ibrahim_chat_id
    _bot_app = bot_app; _ibrahim_chat_id = ibrahim_chat_id

async def _send(message):
    if _bot_app and _ibrahim_chat_id:
        try: await _bot_app.bot.send_message(chat_id=_ibrahim_chat_id, text=message, parse_mode="Markdown")
        except Exception as e: logger.error(f"Scheduler send error: {e}")

def _scout_job(sector):
    try:
        from dynamo.dynamo import dynamo
        result = dynamo.receive(sector.lower().replace(" ","_"), {"lang":"french","auto":True})
        if any(kw in str(result) for kw in ["High","Urgent"]):
            asyncio.run(_send(f"Auto-Scout — {sector}\n---\n{str(result)[:1500]}"))
    except Exception as e: logger.error(f"Scheduler error [{sector}]: {e}")

def _loop():
    global _running; _running = True
    last_run = {s:0 for s in SCHEDULE_HOURS}
    logger.info("Scheduler started")
    while _running:
        now = time.time()
        for sector, interval_h in SCHEDULE_HOURS.items():
            if now - last_run[sector] >= interval_h * 3600:
                last_run[sector] = now; _scout_job(sector)
        time.sleep(60)

def start():
    t = threading.Thread(target=_loop, daemon=True); t.start()
    logger.info("Auto-Scouting Scheduler: ACTIVE"); return t

def stop(): global _running; _running = False
