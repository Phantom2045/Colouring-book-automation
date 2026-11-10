"""Turn the reviewed pages in <folder>/raw into a KDP-ready 8.5x11in PDF (no bleed, blank page after each drawing)."""
import glob, os
from PIL import Image, ImageDraw, ImageFont, ImageOps
import img2pdf

DPI = 300
W, H = int(8.5 * DPI), int(11 * DPI)
MARGIN = int(0.6 * DPI)  # safe margin on all sides


def clean(path):
    im = ImageOps.autocontrast(Image.open(path).convert("L"), cutoff=2)
    im = im.point(lambda p: 255 if p > 215 else (0 if p < 90 else p))
    box = (W - 2 * MARGIN, H - 2 * MARGIN)
    im = ImageOps.contain(im, box, Image.LANCZOS)
    canvas = Image.new("L", (W, H), 255)
    canvas.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    return canvas


def text_page(lines, sizes):
    pg = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(pg)
    y = H // 3
    for line, size in zip(lines, sizes):
        f = ImageFont.load_default(size=size)
        w = d.textlength(line, font=f)
        d.text(((W - w) / 2, y), line, fill=0, font=f)
        y += int(size * 1.8)
    return pg


def build(folder, plan):
    tmp = f"{folder}/tmp"
    os.makedirs(tmp, exist_ok=True)
    files = sorted(glob.glob(f"{folder}/raw/page_*.png"))
    if len(files) < 24:
        raise SystemExit(f"Only {len(files)} pages left; KDP needs at least 24. Generate more or regenerate bad ones.")
    seq = []
    blank = f"{tmp}/blank.png"
    Image.new("L", (W, H), 255).save(blank)
    title = f"{tmp}/title.png"
    text_page([plan["title"][:40], plan.get("subtitle", "")[:50]], [110, 60]).save(title)
    seq += [title, blank]
    for i, f in enumerate(files, 1):
        out = f"{tmp}/p{i:03d}.png"
        clean(f).save(out, dpi=(DPI, DPI))
        seq += [out, blank]
    pdf_path = f"{folder}/interior.pdf"
    layout = img2pdf.get_layout_fun((img2pdf.in_to_pt(8.5), img2pdf.in_to_pt(11)))
    with open(pdf_path, "wb") as fh:
        fh.write(img2pdf.convert(seq, layout_fun=layout))
    print(f"[pdf] {pdf_path} with {len(seq)} pages ({len(files)} drawings)")
    return pdf_path


def contact_sheet(folder, cols=6, thumb=220):
    files = sorted(glob.glob(f"{folder}/raw/page_*.png"))
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb, rows * (thumb + 28)), "white")
    d = ImageDraw.Draw(sheet)
    f = ImageFont.load_default(size=20)
    for i, p in enumerate(files):
        im = ImageOps.contain(Image.open(p).convert("RGB"), (thumb - 6, thumb - 6))
        x, y = (i % cols) * thumb, (i // cols) * (thumb + 28)
        sheet.paste(im, (x + 3, y + 3))
        d.text((x + 6, y + thumb), os.path.basename(p), fill="black", font=f)
    sheet.save(f"{folder}/review_sheet.jpg", quality=85)
