"""Ask Gemini (free tier) to pick ONE narrow niche and write the full book plan as JSON."""
import json, os, re
import requests

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
PAGES = int(os.getenv("BOOK_PAGES", "30"))

PROMPT = """You are a KDP coloring-book publisher.
Trending search phrases (autocomplete):
{keywords}

Niches already published (do NOT repeat): {published}

Pick ONE narrow, specific niche with demand and low saturation (e.g. "bold easy cottagecore animals for seniors").
Rules:
- No trademarks, brands, celebrities, movie/game/anime characters.
- Scenes must be simple enough for clean line art, one clear subject each, all different from each other.
- Return {pages} scenes.

Return ONLY JSON:
{{
 "niche": str,
 "title": str (<=80 chars, keyword-rich),
 "subtitle": str,
 "description": str (150-250 words, plain text, benefit-focused),
 "keywords": [exactly 7 strings, each <=50 chars],
 "audience": str,
 "scenes": [{pages} strings, each a short visual description of one page]
}}"""


def make_plan(keywords, published):
    key = os.environ["GEMINI_API_KEY"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    body = {
        "contents": [{"parts": [{"text": PROMPT.format(
            keywords="\n".join(keywords), published=", ".join(published) or "none", pages=PAGES)}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.9},
    }
    r = requests.post(url, params={"key": key}, json=body, timeout=120)
    r.raise_for_status()
    text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    plan = json.loads(re.sub(r"^```json|```$", "", text.strip()))
    assert len(plan["scenes"]) >= 24, "KDP needs at least 24 pages"
    return plan
