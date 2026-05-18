"""intelligence/cache.py — JSON Cache + Freshness Rules"""
import os, json, time, hashlib
from config import CACHE_DIR, CACHE_DURATION

os.makedirs(CACHE_DIR, exist_ok=True)

def _key(sector, query):
    h = hashlib.md5(f"{sector}:{query}".encode()).hexdigest()[:12]
    return os.path.join(CACHE_DIR, f"{sector}_{h}.json")

def get_cached(sector, query):
    path = _key(sector, query)
    if not os.path.exists(path): return None
    try:
        with open(path) as f: data = json.load(f)
        duration = CACHE_DURATION.get(sector, CACHE_DURATION["default"])
        return data.get("result") if time.time() - data.get("cached_at",0) < duration else None
    except: return None

def set_cache(sector, query, result):
    try:
        with open(_key(sector, query), "w") as f:
            json.dump({"cached_at": time.time(), "result": result}, f, ensure_ascii=False)
    except: pass

def invalidate(sector, query):
    p = _key(sector, query)
    if os.path.exists(p): os.remove(p)
