"""Generate one page per scene. Resumable: skips files that already exist.
To switch image provider, only edit generate_one()."""
import os, time, urllib.parse
import requests

STYLE = ("coloring book page, thick clean black outlines, pure white background, no shading, no grey, "
         "no text, no letters, no watermark, simple large shapes, centered composition, line art")


def generate_one(scene, seed):
    prompt = f"{scene}, {STYLE}"
    url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt) +
           f"?width=1024&height=1280&seed={seed}&model=flux&nologo=true")
    r = requests.get(url, timeout=180)
    r.raise_for_status()
    if "image" not in r.headers.get("content-type", ""):
        raise RuntimeError("not an image response")
    return r.content


def generate_all(plan, folder, delay=8):
    os.makedirs(f"{folder}/raw", exist_ok=True)
    for i, scene in enumerate(plan["scenes"], 1):
        path = f"{folder}/raw/page_{i:02d}.png"
        if os.path.exists(path):
            continue
        for attempt in range(4):
            try:
                data = generate_one(scene, seed=i * 101 + attempt)
                open(path, "wb").write(data)
                print(f"[images] {i}/{len(plan['scenes'])} ok")
                break
            except Exception as e:
                print(f"[images] page {i} attempt {attempt+1} failed: {e}")
                time.sleep(15 * (attempt + 1))
        time.sleep(delay)
