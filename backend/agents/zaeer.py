
def _build_prompt(query, sector, mode, results_text, lang):
    return f"""Analyse ces resultats web REELS:
Query: {query} | Mode: {mode} | Sector: {sector} | Lang: {lang}
RESULTATS:
{results_text}
Extrais l'opportunite la plus pertinente pour BihiApp OS (Maroc/Maghreb focus).
Si resultats insuffisants, baisse la confiance et indique confidence_reason."""


def scout(query="", mode="reactive", sector="all", lang="french", include_social=False):
    if query:
        search_query = query if mode != "reverse" else f"investors looking to buy {query} Morocco"
    else:
        all_q = [q for qs in SEARCH_QUERIES.values() for q in qs] if sector=="all" else SEARCH_QUERIES.get(sector, SEARCH_QUERIES["Real Estate"])
        search_query = random.choice(all_q)

    cached = get_cached(sector if sector!="all" else "default", search_query)
    if cached: return cached

    results = web_search(search_query, num=8)
    if include_social:
        platforms = SOCIAL_PLATFORMS.get(sector, SOCIAL_PLATFORMS["default"])
        for platform in platforms[:2]:
            results += social_search(search_query, platform, sector)

    formatted = format_results(results)
    system_prompt = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["french"])
    prompt = _build_prompt(search_query, sector, mode, formatted, lang)
    raw = route_ai("scout", system_prompt, prompt, max_tokens=1000)
    raw = raw.replace("```json","").replace("```","").strip()

    try:
        data = json.loads(raw)
    except:
        data = {"title":f"Signal: {search_query[:60]}","sector":sector if sector!="all" else "Real Estate",
                "source":"Web Search","summary":f"{len(results)} resultats. Revue manuelle recommandee.",
                "trust_score":35,"risk_score":50,"opportunity_score":40,"confidence":25,
                "priority":"Low","signal_type":mode,"investor_country":None,"investor_profile":None,
                "morocco_relevance":50,"key_urls":[r.get("url","") for r in results[:3]],
                "confidence_reason":"JSON parsing failed"}

    if data.get("confidence",0) < CONFIDENCE_AUTO_FETCH:
        extra_sources = get_sources_for_sector(data.get("sector","Real Estate"))
        if extra_sources:
            extra_results = web_search(f"{search_query} site:{extra_sources[0]}", num=4)
            if extra_results:
                extra_raw = route_ai("scout", system_prompt,
                    _build_prompt(search_query, sector, mode, format_results(extra_results), lang))
                try:
                    extra_data = json.loads(extra_raw.replace("```json","").replace("```","").strip())
                    if extra_data.get("confidence",0) > data.get("confidence",0):
                        data = extra_data
                except: pass

    from legal.legal_engine import inject_legal_context
    legal_ctx = inject_legal_context(data.get("sector",""))
    bb_id = create_opportunity(
        title=data.get("title","Unknown"), sector=data.get("sector","Unknown"),
        source=data.get("source","Web"), summary=data.get("summary",""),
        trust=data.get("trust_score",0), risk=data.get("risk_score",0),
        opportunity=data.get("opportunity_score",0), confidence=data.get("confidence",0),
        priority=data.get("priority","Low"), legal_context=legal_ctx,
    )
    log("Zaeer",f"scout_{mode}_{sector}","Web",f"Signal: {data.get('title','')}","Auto","Saved",False)
    data["dossier_id"] = bb_id
    data["legal_context"] = legal_ctx
    set_cache(sector if sector!="all" else "default", search_query, data)
    return data


def social_scout(query, sector="E-Commerce", lang="french"):
    platforms = SOCIAL_PLATFORMS.get(sector, SOCIAL_PLATFORMS["default"])
    all_results = []
    for platform in platforms:
        all_results += social_search(query, platform, sector)
    if not all_results:
        return scout(query, mode="reactive", sector=sector, lang=lang)
    formatted = format_results(all_results)
    system_prompt = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["french"])
    prompt = f"""Analyse ces resultats RESEAUX SOCIAUX REELS:
Query: {query} | Sector: {sector}
RESULTATS SOCIAL:
{formatted}
Identifie les signaux d'investissement ou opportunites business pertinentes."""
    raw = route_ai("social", system_prompt, prompt, max_tokens=800)
    raw = raw.replace("```json","").replace("```","").strip()
    try:
        data = json.loads(raw)
    except:
        data = {"title":f"Social Signal: {query}","sector":sector,"source":"Social Media",
                "summary":raw[:300],"trust_score":40,"risk_score":50,"opportunity_score":45,
                "confidence":35,"priority":"Low"}
    data["source"] = f"Social Media ({', '.join(platforms)})"
    return data
