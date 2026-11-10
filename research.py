"""Collect trending search phrases from Google + Amazon autocomplete (unofficial endpoints: keep volume low)."""
import time
import requests

SEEDS = [
    "coloring book for adults",
    "coloring book for kids",
    "coloring book for toddlers",
    "coloring book for seniors",
    "coloring book cute",
    "coloring book bold and easy",
]
HEADERS = {"User-Agent": "Mozilla/5.0"}


def google(prefix):
    r = requests.get("https://suggestqueries.google.com/complete/search",
                     params={"client": "firefox", "q": prefix}, headers=HEADERS, timeout=20)
    return r.json()[1]


def amazon(prefix):
    r = requests.get("https://completion.amazon.com/api/2017/suggestions",
                     params={"mid": "ATVPDKIKX0DER", "alias": "aps", "prefix": prefix},
                     headers=HEADERS, timeout=20)
    return [s["value"] for s in r.json().get("suggestions", [])]


def collect_keywords():
    found = {}
    for seed in SEEDS:
        for letter in ["", " a", " b", " c", " f", " m", " s"]:  # a few expansions per seed
            q = seed + letter
            for fn in (google, amazon):
                try:
                    for kw in fn(q):
                        found[kw.lower().strip()] = found.get(kw.lower().strip(), 0) + 1
                except Exception as e:
                    print(f"[research] {fn.__name__} failed for '{q}': {e}")
                time.sleep(0.7)
    # keywords seen in more than one place/seed rank higher
    ranked = sorted(found.items(), key=lambda x: -x[1])
    return [k for k, _ in ranked if "color" in k][:80]
