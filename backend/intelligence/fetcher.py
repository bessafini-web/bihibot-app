"""intelligence/fetcher.py — Web fetch + extract + social media search"""
import requests
from config import SERPER_API_KEY

try:
    from ddgs import DDGS
except ImportError:
    from ddgs import DDGS


def serper_search(query, num=8, gl="ma", hl="fr"):
    if not SERPER_API_KEY: return []
    try:
        r = requests.post("https://google.serper.dev/search",
            headers={"X-API-KEY":SERPER_API_KEY,"Content-Type":"application/json"},
            json={"q":query,"num":num,"gl":gl,"hl":hl}, timeout=10)
        return [{"title":i.get("title",""),"url":i.get("link",""),"body":i.get("snippet","")}
                for i in r.json().get("organic",[])]
    except: return []


def ddg_search(query, num=8):
    try:
        with DDGS() as d:
            return [{"title":r.get("title",""),"url":r.get("href",""),"body":r.get("body","")}
                    for r in d.text(query, max_results=num)]
    except: return []


def web_search(query, num=8):
    results = serper_search(query, num)
    return results if results else ddg_search(query, num)


def fetch_url(url, timeout=10):
    try:
        r = requests.get(url, timeout=timeout,
            headers={"User-Agent":"Mozilla/5.0 (compatible; BihiApp/4.0)"})
        return r.text[:5000]
    except: return ""


def social_search(query, platform="linkedin", sector="real_estate"):
    platform_query = {
        "linkedin":  f"site:linkedin.com {query} investor Morocco",
        "twitter":   f"site:twitter.com OR site:x.com {query} 2025",
        "tiktok":    f"site:tiktok.com {query} trending 2025",
        "instagram": f"site:instagram.com {query} invest",
        "facebook":  f"site:facebook.com {query} Maroc",
        "reddit":    f"site:reddit.com {query} Morocco invest",
        "alibaba":   f"site:alibaba.com OR site:1688.com {query} supplier",
    }.get(platform, f"{query} {platform}")
    return web_search(platform_query, num=5)


def format_results(results):
    if not results: return "No results found."
    return "\n---\n".join([
        f"Title: {r.get('title','')}\nURL: {r.get('url','')}\nSummary: {r.get('body','')[:300]}"
        for r in results[:6]
    ])
