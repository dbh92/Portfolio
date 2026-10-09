"""Vẽ ảnh đại diện 1200x675 cho các bài viết trong src/posts.json.

Mỗi bài có 2 file: <slug>.jpg (og:image, chia sẻ mạng xã hội) và <slug>.webp (hiển thị trên trang, nhẹ hơn).

Chạy:  python tools/make_thumbs.py          (chỉ tạo ảnh còn thiếu)
       python tools/make_thumbs.py --all    (vẽ lại toàn bộ)

Muốn dùng ảnh thật: chép <slug>.jpg vào assets/images/posts/ rồi chạy lại script,
nó sẽ tạo <slug>.webp từ ảnh đó mà không vẽ đè (trừ khi dùng --all).

Font: tools/fonts/BeVietnamPro-*.ttf (SIL OFL 1.1), cùng font với website.
"""
import json
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "assets", "images", "posts")
FONT_DIR = os.path.join(ROOT, "tools", "fonts")
W, H = 1200, 675
INK = (11, 13, 18)
ACCENT = (240, 78, 35)
SYS_FONT_DIRS = ["/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/wqy", r"C:\Windows\Fonts", "/Library/Fonts"]


def font(weight, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, f"BeVietnamPro-{weight}.ttf"), size)


def sys_font(names, size):
    for d in SYS_FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def glyph_font(text, size):
    """Be Vietnam Pro cho chữ Latin/Việt; chữ Hán và ký hiệu toán dùng font hệ thống."""
    if any(0x3000 <= ord(c) <= 0x9FFF for c in text):
        return sys_font(["wqy-zenhei.ttc", "msyhbd.ttc"], size)
    if any(ord(c) > 0x2000 for c in text):
        return sys_font(["DejaVuSans-Bold.ttf", "arialbd.ttf"], size)
    return font("ExtraBold", size)


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def layer():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def blurred(draw_fn, radius):
    lay = layer()
    draw_fn(ImageDraw.Draw(lay))
    return lay.filter(ImageFilter.GaussianBlur(radius))


def grid_layer():
    """Lưới mảnh mờ dần ra rìa."""
    lay = layer()
    d = ImageDraw.Draw(lay)
    for x in range(0, W, 56):
        d.line([(x, 0), (x, H)], fill=(255, 255, 255, 26), width=1)
    for y in range(0, H, 56):
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 26), width=1)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).ellipse((W * .25, -H * .4, W * 1.15, H * .95), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(160))
    lay.putalpha(ImageChops.multiply(lay.getchannel("A"), mask))
    return lay


def fit(text, max_w, max_h, start=300):
    size = start
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    while size > 48:
        f = glyph_font(text, size)
        b = probe.textbbox((0, 0), text, font=f)
        if b[2] - b[0] <= max_w and b[3] - b[1] <= max_h:
            return f, b
        size -= 6
    f = glyph_font(text, size)
    return f, probe.textbbox((0, 0), text, font=f)


def gradient_text(text, f, b, x, y, top, bottom):
    """Chữ tô gradient dọc (trắng → sắc màu chuyên mục)."""
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).text((x - b[0], y - b[1]), text, font=f, fill=255)
    grad = Image.new("RGBA", (W, H))
    gd = ImageDraw.Draw(grad)
    h = max(1, b[3] - b[1])
    for yy in range(H):
        t = min(1, max(0, (yy - y) / h))
        gd.line([(0, yy), (W, yy)], fill=mix(top, bottom, t) + (255,))
    grad.putalpha(mask)
    return grad


def logo_mark(size):
    s = size * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, s - 1, s - 1), radius=int(s * .24), fill=ACCENT + (255,))
    k, w = s / 40, int(3.4 * s / 40)
    for pts in (((11, 13), (6, 20), (11, 27)), ((29, 13), (34, 20), (29, 27)), ((23, 10), (17, 30))):
        d.line([(x * k, y * k) for x, y in pts], fill="white", width=w, joint="curve")
    return im.resize((size, size), Image.LANCZOS)


def render(glyph, chip, c1, c2):
    tint = mix(c1, (255, 255, 255), .25)
    img = Image.new("RGBA", (W, H), mix(c2, INK, .6) + (255,))
    # Quầng sáng màu chuyên mục
    img = Image.alpha_composite(img, blurred(lambda d: d.ellipse((560, -420, 1560, 420), fill=c1 + (215,)), 150))
    img = Image.alpha_composite(img, blurred(lambda d: d.ellipse((-380, 380, 520, 1100), fill=mix(c1, (99, 102, 241), .5) + (90,)), 170))
    img = Image.alpha_composite(img, grid_layer())

    # Vòng tròn đồng tâm bên phải (gợi ống kính / vùng quan sát)
    def rings(d):
        cx, cy = 960, 330
        for r, a in ((140, 46), (220, 30), (300, 18), (380, 10)):
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 255, 255, a), width=2)
        d.ellipse((cx + 214, cy - 62, cx + 230, cy - 46), fill=tint + (230,))
    img = Image.alpha_composite(img, blurred(rings, 0.6))

    # Tối dần phía dưới để chữ nổi
    def shade(d):
        for y in range(H // 2, H):
            d.line([(0, y), (W, y)], fill=(0, 0, 0, int(110 * (y - H / 2) / (H / 2))))
    img = Image.alpha_composite(img, blurred(shade, 0))

    # Chữ lớn
    f, b = fit(glyph, 860, 290)
    gh = b[3] - b[1]
    x, y = 76, 352 - gh / 2
    img = Image.alpha_composite(img, blurred(lambda d: d.text((x - b[0] + 6, y - b[1] + 16), glyph, font=f, fill=(0, 0, 0, 120)), 14))
    img = Image.alpha_composite(img, gradient_text(glyph, f, b, x, y, (255, 255, 255), tint))

    # Nhãn chuyên mục (pill kính mờ)
    d = ImageDraw.Draw(img)
    cf = font("SemiBold", 25)
    cb = d.textbbox((0, 0), chip, font=cf)
    cw = cb[2] - cb[0]
    over = layer()
    od = ImageDraw.Draw(over)
    od.rounded_rectangle((72, 60, 72 + cw + 74, 112), 26, fill=(255, 255, 255, 30), outline=(255, 255, 255, 70), width=2)
    od.ellipse((96, 79, 110, 93), fill=c1 + (255,))
    od.text((124, 86), chip, font=cf, fill=(255, 255, 255, 240), anchor="lm")
    img = Image.alpha_composite(img, over)

    # Thương hiệu
    img.alpha_composite(logo_mark(44), (76, 582))
    d = ImageDraw.Draw(img)
    d.text((134, 604), "hocfree.vn", font=font("SemiBold", 27), fill=(255, 255, 255, 215), anchor="lm")
    return img.convert("RGB")


def save(img, jpg_path, webp=True):
    img.save(jpg_path, "JPEG", quality=86, optimize=True, progressive=True)
    if webp:
        img.save(os.path.splitext(jpg_path)[0] + ".webp", "WEBP", quality=80, method=6)


def main():
    force = "--all" in sys.argv
    with open(os.path.join(ROOT, "src", "posts.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    with open(os.path.join(ROOT, "src", "nav.json"), encoding="utf-8") as fh:
        cats = {s["slug"]: s["label"] for s in json.load(fh)["sections"] if s.get("groups")}
    os.makedirs(OUT_DIR, exist_ok=True)
    for p in data["posts"]:
        jpg = os.path.join(OUT_DIR, p["slug"] + ".jpg")
        webp = os.path.splitext(jpg)[0] + ".webp"
        if force or not os.path.exists(jpg):
            c1, c2 = (hex_rgb(c) for c in p["thumb"]["colors"])
            save(render(p["thumb"]["glyph"], cats[p["category"]], c1, c2), jpg)
            print("  vẽ", os.path.relpath(jpg, ROOT))
        elif not os.path.exists(webp):  # ảnh thật do người dùng chép vào: chỉ tạo bản WebP
            Image.open(jpg).convert("RGB").save(webp, "WEBP", quality=80, method=6)
            print("  webp", os.path.relpath(webp, ROOT))
    og = os.path.join(ROOT, "assets", "images", "og-default.jpg")
    if force or not os.path.exists(og):
        save(render("HọcFree", "Học AI, lập trình & Computer Vision", (240, 78, 35), (122, 29, 12)), og, webp=False)
        print("  vẽ", os.path.relpath(og, ROOT))


if __name__ == "__main__":
    main()
