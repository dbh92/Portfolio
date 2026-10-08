"""Vẽ ảnh đại diện (1200x675 JPG) cho các bài viết trong src/posts.json.

Chạy:  python tools/make_thumbs.py          (chỉ tạo ảnh còn thiếu)
       python tools/make_thumbs.py --all    (vẽ lại toàn bộ)

Muốn dùng ảnh thật: chỉ cần chép file <slug>.jpg vào assets/images/posts/
để thay thế, script sẽ không ghi đè (trừ khi dùng --all).
"""
import json
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "assets", "images", "posts")
W, H = 1200, 675
FONT_DIRS = [r"C:\Windows\Fonts", "/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/wqy", "/Library/Fonts"]


def font(names, size):
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def gradient(c1, c2):
    base = Image.new("RGB", (W, H), c1)
    top = Image.new("RGB", (W, H), c2)
    mask = Image.new("L", (W, H))
    md = mask.load()
    for y in range(H):
        for x in range(0, W, 4):
            v = int(255 * min(1, (x / W) * 0.6 + (y / H) * 0.6))
            for k in range(4):
                if x + k < W:
                    md[x + k, y] = v
    return Image.composite(top, base, mask)


def overlay(img, draw_fn, blur=0):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    if blur:
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(img, layer)


def deco_code(d, rnd):
    """Khung cửa sổ code cho chuyên mục lập trình."""
    x0, y0, x1, y1 = 70, 150, 520, 560
    d.rounded_rectangle((x0, y0, x1, y1), 22, fill=(0, 0, 0, 70), outline=(255, 255, 255, 60), width=2)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse((x0 + 24 + i * 30, y0 + 22, x0 + 42 + i * 30, y0 + 40), fill=c + (230,))
    y = y0 + 75
    while y < y1 - 30:
        indent = rnd.choice([0, 0, 28, 28, 56])
        w = rnd.randint(80, 300 - indent)
        col = rnd.choice([(255, 255, 255, 150), (255, 255, 255, 90), (255, 230, 150, 140)])
        d.rounded_rectangle((x0 + 30 + indent, y, x0 + 30 + indent + w, y + 14), 7, fill=col)
        if rnd.random() < .5:
            w2 = rnd.randint(40, 90)
            d.rounded_rectangle((x0 + 45 + indent + w, y, x0 + 45 + indent + w + w2, y + 14), 7,
                                fill=(140, 220, 255, 140))
        y += 34


def deco_chat(d, rnd):
    """Bong bóng hội thoại cho chuyên mục ngoại ngữ."""
    bubbles = [(70, 170, 430, 270, False), (190, 300, 520, 400, True), (70, 430, 400, 530, False)]
    for x0, y0, x1, y1, right in bubbles:
        fill = (255, 255, 255, 60) if right else (0, 0, 0, 70)
        d.rounded_rectangle((x0, y0, x1, y1), 30, fill=fill, outline=(255, 255, 255, 70), width=2)
        tx = x1 - 40 if right else x0 + 40
        d.polygon([(tx, y1 - 2), (tx + (15 if right else -15), y1 + 26), (tx + (-25 if right else 25), y1 - 2)], fill=fill)
        for j in range(2):
            w = rnd.randint(140, x1 - x0 - 80)
            d.rounded_rectangle((x0 + 35, y0 + 28 + j * 30, x0 + 35 + w, y0 + 42 + j * 30), 7,
                                fill=(255, 255, 255, 150 - j * 50))


def deco_note(d, rnd):
    """Trang sổ tay cho chuyên mục blog."""
    x0, y0, x1, y1 = 80, 140, 500, 570
    d.rounded_rectangle((x0 + 18, y0 + 18, x1 + 18, y1 + 18), 18, fill=(0, 0, 0, 60))
    d.rounded_rectangle((x0, y0, x1, y1), 18, fill=(255, 255, 255, 55), outline=(255, 255, 255, 90), width=2)
    for i in range(7):
        d.ellipse((x0 - 12, y0 + 40 + i * 58, x0 + 12, y0 + 64 + i * 58), fill=(255, 255, 255, 120))
    y = y0 + 60
    d.rounded_rectangle((x0 + 45, y, x0 + 300, y + 22), 10, fill=(255, 255, 255, 200))
    y += 60
    while y < y1 - 30:
        w = rnd.randint(200, x1 - x0 - 90)
        d.rounded_rectangle((x0 + 45, y, x0 + 45 + w, y + 12), 6, fill=(255, 255, 255, 110))
        y += 32


DECOS = {"hoc": deco_code, "projects": deco_code, "ngoai-ngu": deco_chat}  # còn lại: deco_note


def fit_font(draw, text, names, max_w, max_h, start=300):
    size = start
    while size > 40:
        f = font(names, size)
        b = draw.textbbox((0, 0), text, font=f)
        if b[2] - b[0] <= max_w and b[3] - b[1] <= max_h:
            return f, b
        size -= 6
    f = font(names, size)
    return f, draw.textbbox((0, 0), text, font=f)


def make(post, cat_name, path):
    rnd = random.Random(post["slug"])
    c1, c2 = (hex_rgb(c) for c in post["thumb"]["colors"])
    img = gradient(c1, c2).convert("RGBA")

    # Quầng sáng mờ tạo chiều sâu
    def glow(d):
        d.ellipse((650, -200, 1350, 500), fill=(255, 255, 255, 55))
        d.ellipse((-250, 380, 450, 1000), fill=(0, 0, 0, 70))
    img = overlay(img, glow, blur=90)

    # Lưới chấm
    def dots(d):
        for y in range(30, H, 36):
            for x in range(30, W, 36):
                d.ellipse((x - 1.5, y - 1.5, x + 1.5, y + 1.5), fill=(255, 255, 255, 38))
    img = overlay(img, dots)

    img = overlay(img, lambda d: DECOS.get(post["category"], deco_note)(d, rnd))

    # Chữ lớn (glyph)
    glyph = post["thumb"]["glyph"]
    is_cjk = any(ord(ch) > 0x3000 for ch in glyph)
    names = ["msyhbd.ttc", "malgunbd.ttf", "wqy-zenhei.ttc"] if is_cjk else ["seguibl.ttf", "segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"]
    tmp = ImageDraw.Draw(img)
    f, b = fit_font(tmp, glyph, names, 560, 300)
    gw, gh = b[2] - b[0], b[3] - b[1]
    cx, cy = 850, 330
    gx, gy = cx - gw / 2 - b[0], cy - gh / 2 - b[1]
    img = overlay(img, lambda d: d.text((gx + 8, gy + 14), glyph, font=f, fill=(0, 0, 0, 110)), blur=10)
    img = overlay(img, lambda d: d.text((gx, gy), glyph, font=f, fill=(255, 255, 255, 255)))

    # Nhãn chuyên mục + thương hiệu
    def labels(d):
        lf = font(["segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"], 26)
        label = cat_name.upper()
        lb = d.textbbox((0, 0), label, font=lf)
        lw = lb[2] - lb[0]
        d.rounded_rectangle((70, 60, 70 + lw + 40, 108), 24, fill=(255, 255, 255, 235))
        d.text((90, 84), label, font=lf, fill=c2 + (255,), anchor="lm")
        bf = font(["seguibl.ttf", "segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"], 34)
        d.text((1130, 615), "hocfree.vn", font=bf, fill=(255, 255, 255, 220), anchor="rm")
    img = overlay(img, labels)

    img.convert("RGB").save(path, "JPEG", quality=86, optimize=True, progressive=True)


def make_default(path):
    post = {"slug": "default", "category": "hoc",
            "thumb": {"glyph": "HọcFree", "colors": ["#f04e23", "#7a1d0c"]}}
    make(post, "Chia sẻ kiến thức miễn phí", path)


def main():
    force = "--all" in sys.argv
    with open(os.path.join(ROOT, "src", "posts.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    with open(os.path.join(ROOT, "src", "nav.json"), encoding="utf-8") as fh:
        cats = {s["slug"]: s["label"] for s in json.load(fh)["sections"] if s.get("groups")}
    os.makedirs(OUT_DIR, exist_ok=True)
    for p in data["posts"]:
        out = os.path.join(OUT_DIR, p["slug"] + ".jpg")
        if force or not os.path.exists(out):
            make(p, cats[p["category"]], out)
            print("  vẽ", os.path.relpath(out, ROOT))
    og = os.path.join(ROOT, "assets", "images", "og-default.jpg")
    if force or not os.path.exists(og):
        make_default(og)
        print("  vẽ", os.path.relpath(og, ROOT))


if __name__ == "__main__":
    main()
