"""Usage:
  python main.py auto            # research -> plan -> images -> review sheet  (what GitHub Actions runs)
  python main.py pdf books/<dir> # after you delete bad pages from raw/, build interior.pdf
  python main.py images books/<dir>  # re-run to fill in pages you deleted (resumes)
"""
import json, os, re, sys, datetime
import research, plan as planner, images, build_pdf

PUBLISHED = "published.json"


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40]


def load_published():
    return json.load(open(PUBLISHED)) if os.path.exists(PUBLISHED) else []


def auto():
    kws = research.collect_keywords()
    print(f"[research] {len(kws)} keywords")
    p = planner.make_plan(kws[:60], load_published())
    folder = f"books/{datetime.date.today()}_{slug(p['niche'])}"
    os.makedirs(folder, exist_ok=True)
    json.dump(p, open(f"{folder}/plan.json", "w"), indent=2)
    # metadata file you copy-paste into KDP
    open(f"{folder}/kdp_metadata.txt", "w").write(
        f"TITLE: {p['title']}\nSUBTITLE: {p['subtitle']}\n\nKEYWORDS:\n" +
        "\n".join(p["keywords"]) + f"\n\nDESCRIPTION:\n{p['description']}\n")
    images.generate_all(p, folder)
    build_pdf.contact_sheet(folder)
    json.dump(load_published() + [p["niche"]], open(PUBLISHED, "w"), indent=2)
    print(f"[done] {folder}")
    open("latest_folder.txt", "w").write(folder)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "auto"
    if cmd == "auto":
        auto()
    else:
        folder = sys.argv[2]
        p = json.load(open(f"{folder}/plan.json"))
        if cmd == "images":
            images.generate_all(p, folder)
            build_pdf.contact_sheet(folder)
        elif cmd == "pdf":
            build_pdf.build(folder, p)
