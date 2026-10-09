"""Sinh toàn bộ website tĩnh HọcFree từ src/.

  src/posts.json            bài viết, chuyên mục
  src/nav.json              menu chính (mục → nhóm → chủ đề)
  src/learning-paths.json   Learning Paths (lộ trình nghề nghiệp)

Chạy:  python tools/build.py

Thêm bài viết mới:
  1. Thêm một mục vào "posts" trong src/posts.json
  2. Tạo file nội dung src/posts/<slug>.html (chỉ phần thân bài, dùng h2/p/ul/pre…)
  3. python tools/make_thumbs.py   (vẽ ảnh đại diện nếu chưa có ảnh)
  4. python tools/build.py
Bài viết tự xuất hiện trong trang chủ đề nào có "tags" khớp với tag của bài.
"""
import html
import json
import os
import re
import unicodedata
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
VERSION = date.today().strftime("%Y%m%d")

with open(os.path.join(SRC, "posts.json"), encoding="utf-8") as fh:
    DATA = json.load(fh)

SITE = DATA["site"]
POSTS = sorted(DATA["posts"], key=lambda p: p["date"], reverse=True)
BY_SLUG = {p["slug"]: p for p in POSTS}
e = html.escape


# ---------------------------------------------------------------- tiện ích
def slugify(text):
    text = text.replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def fmt_date(iso):
    y, m, d = iso.split("-")
    return f"{d}/{m}/{y}"


def strip_tags(s):
    return re.sub(r"<[^>]+>", " ", s)


def post_url(p):
    return f"{p['category']}/{p['slug']}.html"


def img_url(p):
    """Ảnh hiển thị trên trang (WebP, nhẹ)."""
    return f"assets/images/posts/{p['slug']}.webp"


def og_img(p):
    """Ảnh chia sẻ mạng xã hội / JSON-LD (JPG, tương thích mọi nền tảng)."""
    return f"assets/images/posts/{p['slug']}.jpg"


# Link tải tài liệu (Google Drive…) khai báo một chỗ trong posts.json → "downloads".
# Trong thân bài viết {{download:<key>}} để chèn hộp tải; đổi link chỉ cần sửa posts.json.
DOWNLOADS = DATA.get("downloads", {})


def download_box(key):
    d = DOWNLOADS[key]
    note = "" if d.get("ready") else (
        '<p class="download-note">Bộ tài liệu đang được hoàn thiện, link sẽ mở được khi tài liệu được tải lên.</p>')
    return (f'<div class="download-box"><div class="download-info"><strong>{e(d["label"])}</strong>'
            f'<span>{e(d["desc"])}</span></div>'
            f'<a class="btn" href="{e(d["url"])}" target="_blank" rel="noopener">{e(d.get("cta", "Mở Google Drive"))} →</a>'
            f'{note}</div>')


def load_body(p):
    with open(os.path.join(SRC, "posts", p["slug"] + ".html"), encoding="utf-8") as fh:
        body = fh.read()
    for key in re.findall(r"\{\{download:([\w-]+)\}\}", body):
        assert key in DOWNLOADS, f"Bài {p['slug']}: không có downloads.{key} trong posts.json"
        body = body.replace("{{download:%s}}" % key, download_box(key))
    return body


# ---------------------------------------------------------------- menu & lộ trình
with open(os.path.join(SRC, "nav.json"), encoding="utf-8") as fh:
    NAV = json.load(fh)
with open(os.path.join(SRC, "learning-paths.json"), encoding="utf-8") as fh:
    PATHS = json.load(fh)["paths"]

SECTIONS = NAV["sections"]
SEC = {s["key"]: s for s in SECTIONS}
JOURNEY = sorted((s for s in SECTIONS if s.get("step")), key=lambda s: s["step"])
PATH_BY = {p["slug"]: p for p in PATHS}

# Chuyên mục của bài viết = một mục menu có chủ đề (hoc, projects, kien-thuc, tin-tuc-ai, ngoai-ngu, tai-nguyen).
# Bài nằm ở <mục>/<slug>.html, cùng thư mục với trang chủ đề của mục đó.
CATS = {s["slug"]: {"slug": s["slug"], "name": s["label"], "section": s["key"]} for s in SECTIONS if s.get("groups")}

for _p in POSTS:
    _p["body"] = load_body(_p)
    _words = len(strip_tags(_p["body"]).split())
    _p["minutes"] = max(1, -(-_words // 180))  # ~180 từ/phút, làm tròn lên
    assert _p["category"] in CATS, f"Bài {_p['slug']}: category phải là một trong {sorted(CATS)}"
    _p["cat"] = CATS[_p["category"]]


def section_url(sec):
    """URL thư mục (hoc/, lo-trinh/…) trùng với canonical; trang chủ là chuỗi rỗng."""
    if "href" in sec:
        return "" if sec["href"] == "index.html" else sec["href"]
    return f"{sec.get('category') or sec['slug']}/"


def link(root, rel=""):
    """Ghép đường dẫn tương đối; rỗng (trang chủ từ trang chủ) thành ./"""
    return f"{root}{rel}" or "./"


def path_url(p):
    return f"lo-trinh/{p['slug']}.html" if p.get("steps") else f"lo-trinh/#{p['slug']}"


def match_posts(item):
    """Bài thuộc chủ đề: có tag khớp (nếu khai báo tags) và nằm trong categories (nếu khai báo)."""
    tags = {t.lower() for t in item.get("tags", [])}
    cats = set(item.get("categories", []))
    if not tags and not cats:
        return []
    return [p for p in POSTS
            if (not cats or p["category"] in cats)
            and (not tags or tags & {t.lower() for t in p["tags"]})]


TOPICS = []
for _s in SECTIONS:
    for _g in _s.get("groups", []):
        for _i in _g["items"]:
            TOPICS.append({
                "ref": f"{_s['slug']}/{_i['slug']}", "url": _i.get("href") or f"{_s['slug']}/{_i['slug']}.html",
                "sec": _s, "group": _g, "item": _i, "posts": match_posts(_i),
            })
TOPIC_BY = {t["ref"]: t for t in TOPICS}


def section_posts(sec):
    """Bài thuộc một mục menu: nằm trong mục đó hoặc khớp một chủ đề của mục."""
    refs = {id(p) for t in TOPICS if t["sec"] is sec for p in t["posts"]}
    return [p for p in POSTS if p["category"] == sec.get("slug") or id(p) in refs]
assert len(TOPIC_BY) == len(TOPICS), "Trùng slug chủ đề trong src/nav.json"
assert not {t["url"] for t in TOPICS} & {f"{p['category']}/{p['slug']}.html" for p in POSTS}, \
    "Slug chủ đề trùng với slug bài viết"

# chủ đề → các chặng lộ trình có nhắc tới nó (để gợi ý "Có trong lộ trình")
TOPIC_IN_PATH = {}
for _p in PATHS:
    for _n, _st in enumerate(_p.get("steps", []), 1):
        for _ref in _st["topics"]:
            assert _ref in TOPIC_BY, f"Lộ trình {_p['slug']}: chủ đề {_ref} không có trong nav.json"
            TOPIC_IN_PATH.setdefault(_ref, []).append((_p, _n, _st))


def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    print("  ghi", rel)


# ---------------------------------------------------------------- khung trang
LOGO = """<svg class="logo-mark" viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="10" fill="var(--accent)"/><path d="M11 13l-5 7 5 7M29 13l5 7-5 7M23 10l-6 20" stroke="#fff" stroke-width="3.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

ICON = {
    "search": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>',
    "moon": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
    "close": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    "cal": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>',
    "fb": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 8h3V4h-3a4 4 0 0 0-4 4v2H8v4h2v6h4v-6h3l1-4h-4V8z"/></svg>',
    "x": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 4l16 16M20 4L4 20"/></svg>',
    "link": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 14a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/><path d="M14 10a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/></svg>',
    "up": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 15l6-6 6 6"/></svg>',
    "chev": '<svg class="chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>',
}


with open(os.path.join(SRC, "icons.json"), encoding="utf-8") as fh:
    ICONS = json.load(fh)["icons"]


def icon(name, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<svg{c} viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


def ld_json(*objs):
    """Một hoặc nhiều khối JSON-LD (schema.org)."""
    return "".join(f'<script type="application/ld+json">{json.dumps(o, ensure_ascii=False)}</script>\n' for o in objs)


def breadcrumb_ld(items):
    """items: [(tên, url tương đối hoặc None cho trang hiện tại)], không gồm Trang chủ."""
    trail = [("Trang chủ", "")] + items
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": n, **({"item": f"{SITE['domain']}/{u}"} if u is not None else {})}
        for i, (n, u) in enumerate(trail, 1)]}


ORG = {"@type": "Organization", "name": SITE["name"], "url": SITE["domain"] + "/",
       "logo": {"@type": "ImageObject", "url": f"{SITE['domain']}/assets/images/icon-512.png", "width": 512, "height": 512}}

# Font chính (Be Vietnam Pro 400 + 800, latin + vietnamese) tải sớm để chữ không nhảy
PRELOAD_FONTS = ["be-vietnam-pro-latin-400-normal", "be-vietnam-pro-vietnamese-400-normal", "be-vietnam-pro-latin-800-normal"]


def head(root, title, desc, canonical, image, og_type="website", extra="", robots=None):
    robots = robots or "index, follow, max-image-preview:large"
    if title == SITE["name"]:
        full_title = f"{SITE['name']} – {SITE['tagline']}"
    else:  # tiêu đề dài thì bỏ hậu tố tên site để Google không cắt mất nội dung chính
        full_title = f"{title} | {SITE['name']}" if len(title) <= 58 else title
    img_abs = f"{SITE['domain']}/{image}"
    url_abs = f"{SITE['domain']}/{canonical}"
    preload = "".join(f'<link rel="preload" href="{root}assets/fonts/{f}.woff2" as="font" type="font/woff2" crossorigin>\n'
                      for f in PRELOAD_FONTS)
    return f"""<!DOCTYPE html>
<html lang="vi" data-root="{root}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url_abs}">
<meta property="og:site_name" content="{e(SITE['name'])}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url_abs}">
<meta property="og:image" content="{img_abs}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="675">
<meta property="og:image:alt" content="{e(title)}">
<meta property="og:locale" content="vi_VN">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{img_abs}">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0a0b0f" media="(prefers-color-scheme: dark)">
<link rel="icon" href="{root}assets/images/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{root}assets/images/apple-touch-icon.png">
<link rel="manifest" href="{root}site.webmanifest">
{preload}<link rel="stylesheet" href="{root}assets/css/fonts.css?v={VERSION}">
<link rel="stylesheet" href="{root}assets/css/style.css?v={VERSION}">
<script>try{{var t=localStorage.getItem('hf-theme');if(t==='dark'||(!t&&matchMedia('(prefers-color-scheme: dark)').matches))document.documentElement.classList.add('dark')}}catch(e){{}}</script>
{extra}</head>
<body>
<a class="skip-link" href="#main">Bỏ qua đến nội dung</a>
"""


def journey(root, current=None, cls=""):
    """Dải 3 bước HỌC → THỰC HÀNH → TRỞ THÀNH KỸ SƯ, dùng ở mega menu và các trang hub."""
    lis = ""
    for s in JOURNEY:
        cur = ' aria-current="step"' if s["key"] == current else ""
        lis += (f'<li><a href="{link(root, section_url(s))}"{cur}><span class="journey-n">{s["step"]}</span>'
                f'<span class="journey-t"><b>{e(s["stepLabel"])}</b><small>{e(s["label"])}</small></span></a></li>')
    return f'<ol class="journey {cls}" aria-label="Học, thực hành, trở thành kỹ sư">{lis}</ol>'


def feature_card(root, p, big=False):
    """Card nổi bật cho Learning Path flagship (Vision Engineer)."""
    arrow = '<i aria-hidden="true">→</i>'
    chain = "".join(f"<span>{e(x)}</span>{arrow}" for x in p["preview"]) + f'<span class="chain-goal">🎯 {e(p["short"])}</span>'
    n_steps, n_phases = len(p["steps"]), len(p["phases"])
    return f"""<a class="feature-card{' big' if big else ''}" href="{root}{path_url(p)}">
  <span class="feature-eyebrow">⭐ Learning Path nổi bật</span>
  <span class="feature-title">{e(p['label'])}</span>
  <span class="feature-sub">{e(p['tagline'])}</span>
  <span class="feature-desc">{e(p['description'])}</span>
  <span class="feature-chain" aria-label="Các chặng chính">{chain}</span>
  <span class="feature-meta">{n_steps} chặng · {n_phases} giai đoạn · {e(p['duration'])}</span>
  <span class="feature-cta">Xem lộ trình →</span>
</a>"""


def _panel_kicker(sec):
    if not sec.get("step"):
        return ""
    return f'<p class="panel-kicker"><span>Bước {sec["step"]} · {e(sec["stepLabel"])}</span>{e(sec["stepDesc"])}</p>'


def nav_panel(root, sec):
    pid = f"nav-panel-{sec['key']}"
    all_link = f'<a class="panel-all" href="{link(root, section_url(sec))}">Xem tất cả {e(sec["label"])} →</a>'

    if sec.get("layout") == "mega":
        groups = ""
        for g in sec["groups"]:
            lis = "".join(f'<li><a href="{root}{TOPIC_BY[sec["slug"] + "/" + i["slug"]]["url"]}">{e(i["label"])}</a></li>'
                          for i in g["items"])
            groups += (f'<div class="mega-group"><a class="mega-group-title" href="{link(root, section_url(sec))}#{g["slug"]}">'
                       f'{e(g["label"])}</a><ul>{lis}</ul></div>')
        return f"""<div class="nav-panel mega" id="{pid}">
  <div class="container wide mega-inner">
    <div class="mega-groups">{groups}</div>
    {feature_card(root, PATH_BY[sec['featured']])}
  </div>
  <div class="mega-foot"><div class="container wide mega-foot-inner">{journey(root, sec['key'], 'compact')}{all_link}</div></div>
</div>"""

    if sec.get("layout") == "paths":
        lis = ""
        for p in PATHS:
            if p.get("flagship"):
                lis += (f'<li><a class="drop-link is-flagship" href="{root}{path_url(p)}"><span class="drop-label">⭐ {e(p["label"])}</span>'
                        f'<span class="drop-desc">{e(p["tagline"])} · {len(p["steps"])} chặng</span></a></li>')
            else:
                lis += (f'<li><a class="drop-link" href="{root}{path_url(p)}"><span class="drop-label">{e(p["label"])}'
                        f'<span class="badge-soon">Sắp ra mắt</span></span><span class="drop-desc">{e(p["tagline"])}</span></a></li>')
        return f"""<div class="nav-panel drop" id="{pid}">
  {_panel_kicker(sec)}
  <ul class="drop-list">{lis}</ul>
  <a class="panel-all" href="{link(root, section_url(sec))}">Xem tất cả lộ trình →</a>
</div>"""

    groups = sec["groups"]
    cols = ""
    for g in groups:
        title = f'<p class="drop-group-title">{e(g["label"])}</p>' if len(groups) > 1 else ""
        lis = ""
        for i in g["items"]:
            t = TOPIC_BY[f"{sec['slug']}/{i['slug']}"]
            desc = f'<span class="drop-desc">{e(i["desc"])}</span>' if i.get("desc") else ""
            lis += f'<li><a class="drop-link" href="{root}{t["url"]}"><span class="drop-label">{e(i["label"])}</span>{desc}</a></li>'
        cols += f'<div class="drop-col">{title}<ul class="drop-list">{lis}</ul></div>'
    wide = " wide" if len(groups) > 1 else ""
    return f"""<div class="nav-panel drop{wide}" id="{pid}">
  {_panel_kicker(sec)}
  <div class="drop-cols">{cols}</div>
  {all_link}
</div>"""


def header(root, active=""):
    items = ""
    for sec in SECTIONS:
        cur = sec["key"] == active
        act = " is-active" if cur else ""
        if "groups" not in sec and sec.get("layout") != "paths":
            aria = ' aria-current="page"' if cur else ""
            items += f'<li class="nav-item"><a class="nav-link{act}" href="{link(root, section_url(sec))}"{aria}>{e(sec["label"])}</a></li>'
            continue
        cls = "nav-item has-panel"
        cls += " is-mega" if sec.get("layout") == "mega" else ""
        cls += " align-end" if sec.get("align") == "end" else ""
        aria = ' aria-current="true"' if cur else ""
        items += (f'<li class="{cls}"><button type="button" class="nav-link nav-trigger{act}"'
                  f' aria-expanded="false" aria-controls="nav-panel-{sec["key"]}"{aria}>'
                  f'{e(sec["label"])}{ICON["chev"]}</button>{nav_panel(root, sec)}</li>')

    start = f"{root}lo-trinh/"
    login = f"{root}dang-nhap.html"
    return f"""<div class="progress" aria-hidden="true"></div>
<header class="site-header">
  <div class="container wide header-top">
    <button class="icon-btn burger" aria-label="Mở menu" aria-expanded="false" aria-controls="site-nav">{ICON['menu']}</button>
    <div class="nav-scrim" hidden></div>
    <a class="logo" href="{link(root)}" aria-label="{e(SITE['name'])} – Trang chủ">{LOGO}<span>Học<b>Free</b></span></a>
    <button type="button" class="search-trigger search-open" aria-label="Tìm kiếm (Ctrl + K)">{ICON['search']}<span class="search-trigger-text">Tìm bài học, chủ đề, bài viết…</span><kbd>Ctrl K</kbd></button>
    <div class="header-actions">
      <button class="icon-btn theme-toggle" aria-label="Đổi giao diện sáng/tối">{ICON['moon']}</button>
      <a class="login-link" href="{login}">Đăng nhập</a>
      <a class="btn start-btn" href="{start}">Bắt đầu học</a>
    </div>
  </div>
  <div class="header-nav">
    <div class="container wide">
      <nav class="site-nav" id="site-nav" aria-label="Menu chính">
        <div class="drawer-head">
          <a class="logo" href="{link(root)}" tabindex="-1">{LOGO}<span>Học<b>Free</b></span></a>
          <button class="icon-btn nav-close" aria-label="Đóng menu">{ICON['close']}</button>
        </div>
        <button type="button" class="drawer-search search-open">{ICON['search']}<span>Tìm bài học, chủ đề…</span></button>
        <ul class="nav-list">{items}</ul>
        <div class="drawer-foot">
          <a class="btn ghost" href="{login}">Đăng nhập</a>
          <a class="btn" href="{start}">Bắt đầu học</a>
        </div>
      </nav>
    </div>
  </div>
</header>
{search_dialog(root)}
"""


def search_dialog(root):
    chips = "".join(f'<a class="chip" href="{root}{TOPIC_BY[r]["url"]}">{e(TOPIC_BY[r]["item"]["label"])}</a>'
                    for r in NAV["popularTopics"])
    flag = next(p for p in PATHS if p.get("flagship"))
    return f"""<div class="search-dialog" hidden>
  <div class="search-scrim"></div>
  <div class="search-box" role="dialog" aria-modal="true" aria-label="Tìm kiếm">
    <form class="search-form" action="{root}search.html" role="search">
      {ICON['search']}
      <input type="search" name="q" placeholder="Tìm bài học, chủ đề, bài viết…" autocomplete="off" aria-label="Từ khóa tìm kiếm" aria-controls="search-suggest">
      <button type="button" class="icon-btn search-close" aria-label="Đóng">{ICON['close']}</button>
    </form>
    <div class="search-suggest" id="search-suggest" aria-live="polite">
      <div class="search-empty">
        <p class="search-group-title">Chủ đề phổ biến</p>
        <div class="chips">{chips}</div>
        <p class="search-group-title">Lộ trình nổi bật</p>
        <a class="search-item" href="{root}{path_url(flag)}"><span class="search-ico" aria-hidden="true">⭐</span><span>{e(flag['label'])}<small>Learning Path · {e(flag['tagline'])}</small></span></a>
      </div>
    </div>
    <div class="search-foot" aria-hidden="true"><span><kbd>↑</kbd><kbd>↓</kbd> chọn</span><span><kbd>Enter</kbd> mở</span><span><kbd>Esc</kbd> đóng</span></div>
  </div>
</div>"""


def footer(root):
    def col(title, secs):
        lis = "".join(f'<li><a href="{link(root, section_url(s))}">{e(s["label"])}</a></li>' for s in secs)
        return f"<div><h3>{title}</h3><ul>{lis}</ul></div>"
    learn = col("Học &amp; thực hành", JOURNEY)
    explore = col("Khám phá", [s for s in SECTIONS if s.get("groups") and not s.get("step")])
    latest = "".join(f'<li><a href="{root}{post_url(p)}">{e(p["title"])}</a></li>' for p in POSTS[:4])
    latest = f"<div><h3>Bài mới</h3><ul>{latest}</ul></div>" if latest else ""
    year = date.today().year
    return f"""<footer class="site-footer">
  <div class="container footer-grid">
    <div class="footer-about">
      <a class="logo" href="{link(root)}">{LOGO}<span>Học<b>Free</b></span></a>
      <p>{e(SITE['description'])}</p>
    </div>
    {learn}
    {explore}
    {latest}
    <div>
      <h3>HọcFree</h3>
      <ul>
        <li><a href="{root}gioi-thieu.html">Giới thiệu</a></li>
        <li><a href="{root}search.html">Tìm kiếm</a></li>
        <li><a href="{root}sitemap.xml">Sitemap</a></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">
    <div class="container">© {year} HọcFree.vn · Kiến thức là để chia sẻ.</div>
  </div>
</footer>
<button class="to-top" aria-label="Lên đầu trang">{ICON['up']}</button>
<script src="{root}assets/js/search-data.js?v={VERSION}" defer></script>
<script src="{root}assets/js/main.js?v={VERSION}" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------- thành phần
def cat_pill(root, p, cls="pill"):
    return f'<a class="{cls} cat-{p["category"]}" href="{root}{p["category"]}/">{e(p["cat"]["name"])}</a>'


def meta(p, author=False):
    a = f'<span class="by">{e(SITE["author"])}</span>' if author else ""
    return (f'<div class="meta">{a}<span>{ICON["cal"]}<time datetime="{p["date"]}">{fmt_date(p["date"])}</time></span>'
            f'<span>{ICON["clock"]}{p["minutes"]} phút đọc</span></div>')


def post_row(root, p):
    return f"""<article class="post-row">
  <a class="thumb" href="{root}{post_url(p)}" tabindex="-1" aria-hidden="true"><img src="{root}{img_url(p)}" alt="" width="1200" height="675" loading="lazy"></a>
  <div class="post-row-body">
    {cat_pill(root, p, "kicker")}
    <h3><a href="{root}{post_url(p)}">{e(p['title'])}</a></h3>
    <p>{e(p['excerpt'])}</p>
    {meta(p, author=True)}
  </div>
</article>"""


def card(root, p):
    return f"""<article class="card">
  <a class="thumb" href="{root}{post_url(p)}" tabindex="-1" aria-hidden="true"><img src="{root}{img_url(p)}" alt="" width="1200" height="675" loading="lazy"></a>
  {cat_pill(root, p, "kicker")}
  <h3><a href="{root}{post_url(p)}">{e(p['title'])}</a></h3>
  {meta(p)}
</article>"""


def sidebar(root, current=None):
    popular = [BY_SLUG[x] for x in DATA.get("popular", []) if x in BY_SLUG and x != current][:5]
    pop = "".join(
        f'<li><a href="{root}{post_url(p)}"><span class="num">{i}</span><span class="t">{e(p["title"])}</span></a></li>'
        for i, p in enumerate(popular, 1))
    secs = "".join(
        f'<li><a href="{link(root, section_url(s))}"><span>{e(s["label"])}</span>'
        f'<span class="count">{count_label(len(section_posts(s)))}</span></a></li>'
        for s in SECTIONS if s.get("groups"))
    tags = sorted({t for p in POSTS for t in p["tags"]}, key=str.lower)
    tag_html = "".join(f'<a class="tag" href="{root}search.html?q={e(t)}">{e(t)}</a>' for t in tags)
    pop_w = f'<section class="widget"><h2 class="widget-title">Đọc nhiều nhất</h2><ol class="popular">{pop}</ol></section>' if pop else ""
    tag_w = f'<section class="widget"><h2 class="widget-title">Thẻ</h2><div class="tags">{tag_html}</div></section>' if tags else ""
    return f"""<aside class="sidebar">
  {pop_w}
  <section class="widget">
    <h2 class="widget-title">Chuyên mục</h2>
    <ul class="cat-list">{secs}</ul>
  </section>
  <section class="widget widget-about">
    <h2 class="widget-title">Về HọcFree</h2>
    <p>Nơi học <strong>miễn phí</strong> AI, lập trình, Computer Vision và ngoại ngữ dành cho người Việt. Không quảng cáo, không thu phí.</p>
    <a class="btn" href="{root}gioi-thieu.html">Tìm hiểu thêm</a>
  </section>
  {tag_w}
</aside>"""


def section_title(text, link=None, root=""):
    more = f'<a class="more" href="{root}{link}">Xem tất cả →</a>' if link else ""
    return f'<div class="section-title"><h2>{e(text)}</h2>{more}</div>'


# ---------------------------------------------------------------- trang chủ
# Hình mô phỏng màn hình kiểm tra Vision (trang trí, aria-hidden): băng tải, 3 bo mạch, khung OK/NG
def _pcb(x, y, scratch=False):
    pads = "".join(f'<circle cx="{x + dx}" cy="{y + dy}" r="4" fill="#d4b26a"/>' for dx, dy in ((12, 12), (108, 12), (12, 76), (108, 76)))
    pins = "".join(f'<rect x="{x + 45 + i * 8}" y="{y + 22}" width="3" height="6" fill="#c9a24b"/><rect x="{x + 45 + i * 8}" y="{y + 60}" width="3" height="6" fill="#c9a24b"/>' for i in range(4))
    traces = (f'<path d="M{x + 16} {y + 44}H{x + 42}M{x + 78} {y + 44}H{x + 104}M{x + 60} {y + 66}V{y + 80}" stroke="#3fa57f" stroke-width="2.5" fill="none"/>')
    cut = (f'<path d="M{x + 70} {y + 14}l10 9-6 4 12 10-5 3 9 9" stroke="#ff6b6b" stroke-width="3" fill="none" stroke-linecap="round"/>'
           if scratch else "")
    return (f'<rect x="{x}" y="{y}" width="120" height="88" rx="8" fill="#1d6b51" stroke="#2c8a69" stroke-width="2"/>{traces}{pads}{pins}'
            f'<rect x="{x + 42}" y="{y + 27}" width="36" height="34" rx="4" fill="#0e1117"/>{cut}')


def _box(x, y, w, ok, label):
    c, tc = ("#4ade80", "#052e16") if ok else ("#f87171", "#450a0a")
    return (f'<rect x="{x}" y="{y}" width="{w}" height="106" rx="6" fill="none" stroke="{c}" stroke-width="2.5"/>'
            f'<rect x="{x - 1.25}" y="{y - 24}" width="{len(label) * 7.6 + 16}" height="22" rx="5" fill="{c}"/>'
            f'<text x="{x + 7}" y="{y - 8.5}" font-size="12.5" fill="{tc}">{label}</text>')


def vision_mock():
    belt = "".join(f'<path d="M{x} 300l26-60" stroke="#1f2633" stroke-width="10"/>' for x in range(-20, 640, 36))
    scene = (
        '<svg viewBox="0 0 600 320" role="presentation">'
        '<rect width="600" height="320" fill="#0c1018"/>'
        '<path d="M300 44 120 236M300 44 480 236" stroke="rgba(255,255,255,.12)" stroke-dasharray="4 6"/>'
        '<rect x="276" y="14" width="48" height="30" rx="6" fill="#2a3242"/><circle cx="300" cy="44" r="9" fill="#11151d" stroke="#3b4456" stroke-width="3"/>'
        '<text x="18" y="28" font-size="11" fill="#6f7686">CAM 0 · frame 1284</text>'
        '<text x="582" y="28" font-size="11" fill="#6f7686" text-anchor="end">YOLO26 · 640px</text>'
        f'<g><rect y="236" width="600" height="84" fill="#151a24"/>{belt}<rect y="236" width="600" height="3" fill="#2a3242"/></g>'
        + _pcb(40, 140) + _pcb(240, 140, scratch=True) + _pcb(440, 140)
        + _box(32, 132, 136, True, "OK 0.98") + _box(232, 132, 136, False, "NG · scratch 0.91") + _box(432, 132, 136, True, "OK 0.97")
        + "</svg>")
    code = ('<span class="k">from</span> ultralytics <span class="k">import</span> YOLO\n'
            'model = YOLO(<span class="s">"hocfree-defect.pt"</span>)\n'
            '<span class="k">for</span> r <span class="k">in</span> model(<span class="s">"cam0"</span>, stream=<span class="k">True</span>):\n'
            '    plc.send(r.verdict)  <span class="c"># OK / NG</span>')
    return f"""<div class="hx-visual" aria-hidden="true">
        <div class="mock">
          <div class="mock-bar"><i></i><i></i><i></i><span>inspection.py — HọcFree Vision</span><b class="mock-live">LIVE</b></div>
          <div class="mock-view">{scene}<span class="mock-scan"></span></div>
        </div>
        <pre class="mock-code">{code}</pre>
        <div class="mock-metric"><span class="mm-ico">{icon("check")}</span><div><b>99,2%</b><small>chính xác</small></div><div><b>38 ms</b><small>mỗi sản phẩm</small></div></div>
      </div>"""


TOPIC_ICON = {"hoc/python": "code-xml", "hoc/opencv": "scan-eye", "hoc/machine-vision": "camera", "hoc/deep-learning": "brain",
              "hoc/ai-vision": "scan-search", "hoc/object-detection": "box-select", "hoc/pytorch": "flame", "ngoai-ngu/english": "languages"}


def sec_head(eyebrow, title, sub="", more=None, center=False, hid=""):
    more_html = f'<a class="more" href="{more[1]}">{e(more[0])}{icon("arrow-right")}</a>' if more else ""
    sub_html = f'<p class="sub">{e(sub)}</p>' if sub else ""
    return (f'<div class="sec-head{" center" if center else ""}"><div><p class="eyebrow">{e(eyebrow)}</p>'
            f'<h2 id="{hid}">{title}</h2>{sub_html}</div>{more_html}</div>')


def build_home():
    """Trang chủ: hero tối có mô phỏng Vision, 3 bước, lộ trình nổi bật, chủ đề, bài mới, khám phá, CTA."""
    root = ""
    flag = next(p for p in PATHS if p.get("flagship"))
    steps = flag["steps"]

    flow_data = [  # (mục, icon, mô tả, chữ nút)
        (SEC["hoc"], "book-open", "Python, AI, Computer Vision và Machine Vision, từ nền tảng đến chuyên sâu.", "Vào học"),
        (SEC["projects"], "code-xml", "Dự án có mã nguồn: đo kích thước, đọc mã, phát hiện lỗi trên dây chuyền.", "Xem dự án"),
        (SEC["lo-trinh"], "graduation-cap", "Lộ trình nghề nghiệp rõ ràng: biết mình ở đâu và cần học gì tiếp.", "Xem lộ trình"),
    ]
    flow = "".join(f"""<li><a class="flow-card" href="{section_url(sec)}">
          <span class="ico-tile">{icon(ic)}</span><span class="flow-n">0{sec['step']}</span>
          <h3>{e(sec['stepLabel'])}</h3><p>{e(desc)}</p>
          <span class="flow-link">{e(cta)}{icon("arrow-right")}</span></a></li>""" for sec, ic, desc, cta in flow_data)

    phases = ""
    for n, ph in enumerate(flag["phases"], 1):
        ph_steps = [st for st in steps if st["phase"] == ph["slug"]]
        phases += (f'<li><span class="pn">{n}</span><div><b>{e(ph["label"])}</b>'
                   f'<small>{" · ".join(e(st["title"]) for st in ph_steps)}</small></div>'
                   f'<span class="wk">{sum(st["weeks"] for st in ph_steps)} tuần</span></li>')
    phases += f'<li class="goal-row"><span class="pn">🎯</span><div><b>{e(flag["goal"]["title"])}</b><small>{e(", ".join(flag["goal"]["roles"][:3]))}</small></div></li>'

    tiles = "".join(
        f'<a class="topic-tile" href="{TOPIC_BY[r]["url"]}"><span class="ico">{icon(TOPIC_ICON.get(r, "sparkles"))}</span>'
        f'<span><b>{e(TOPIC_BY[r]["item"]["label"])}</b><small>{len(TOPIC_BY[r]["posts"])} bài viết</small></span></a>'
        for r in NAV["popularTopics"])

    # 5 bài mới nhất, tối đa 2 bài mỗi mục để trang chủ không bị một mục chiếm hết
    picked, per_cat = [], {}
    for p in POSTS:
        if per_cat.get(p["category"], 0) < 2:
            picked.append(p)
            per_cat[p["category"]] = per_cat.get(p["category"], 0) + 1
        if len(picked) == 5:
            break
    f0 = picked[0]
    feature = f"""<a class="mag-feature" href="{post_url(f0)}">
        <span class="mag-img"><img src="{img_url(f0)}" alt="{e(f0['title'])}" width="1200" height="675" loading="lazy" decoding="async"></span>
        <span class="kicker">{e(f0['cat']['name'])}</span><h3>{e(f0['title'])}</h3><p>{e(f0['excerpt'])}</p>
        <span class="meta"><span>{icon("calendar")}{fmt_date(f0['date'])}</span><span>{icon("clock")}{f0['minutes']} phút đọc</span></span></a>"""
    items = "".join(f"""<a class="mag-item" href="{post_url(p)}"><span class="im"><img src="{img_url(p)}" alt="" width="1200" height="675" loading="lazy" decoding="async"></span>
        <span><span class="kicker">{e(p['cat']['name'])}</span><b>{e(p['title'])}</b><small>{fmt_date(p['date'])} · {p['minutes']} phút đọc</small></span></a>"""
                    for p in picked[1:])

    explore_data = [("kien-thuc", "library", "Giải thích khái niệm, công cụ và mẹo hay."),
                    ("tin-tuc-ai", "newspaper", "Tin AI, mô hình mới và Robotics chọn lọc."),
                    ("ngoai-ngu", "languages", "Lộ trình 700 TOEIC và HSK3 cho người đi làm."),
                    ("tai-nguyen", "folder-open", "Cheat sheet, dataset, mã nguồn và sách hay.")]
    explore = "".join(f"""<a class="ex-card" href="{section_url(SEC[k])}"><span class="ico-tile">{icon(ic)}</span>
        <h3>{e(SEC[k]['label'])}</h3><p>{e(desc)}</p><span class="count">{len(section_posts(SEC[k]))} bài viết →</span></a>"""
                      for k, ic, desc in explore_data)

    stack = "".join(f"<li>{x}</li>" for x in ["Python", "OpenCV", "PyTorch", "YOLO", "ONNX Runtime", "C# .NET", "OPC UA"])

    ld = ld_json(
        {"@context": "https://schema.org", "@type": "WebSite", "name": SITE["name"], "url": SITE["domain"] + "/", "inLanguage": "vi",
         "description": SITE["description"], "publisher": ORG,
         "potentialAction": {"@type": "SearchAction", "target": {"@type": "EntryPoint", "urlTemplate": f"{SITE['domain']}/search.html?q={{search_term_string}}"},
                             "query-input": "required name=search_term_string"}},
        {"@context": "https://schema.org", **ORG})
    page = head(root, SITE["name"], SITE["description"], "", "assets/images/og-default.jpg", extra=ld)
    page += header(root, active="home")
    page += f"""<main id="main">
  <section class="hx">
    <div class="container hx-inner">
      <div class="hx-copy">
        <a class="hx-badge" href="{path_url(flag)}"><b>Mới</b>Lộ trình Vision Engineer {len(steps)} chặng →</a>
        <h1>Học AI &amp; Computer Vision <span class="grad-text">từ số 0 đến kỹ sư</span></h1>
        <p class="hx-sub">Bài học tiếng Việt dễ hiểu, dự án có mã nguồn và lộ trình rõ ràng để trở thành Vision Engineer. Hoàn toàn miễn phí.</p>
        <div class="hx-cta">
          <a class="btn lg" href="{section_url(SEC['hoc'])}">Bắt đầu học miễn phí{icon("arrow-right")}</a>
          <a class="btn lg ghost-light" href="{path_url(flag)}">Xem lộ trình</a>
        </div>
        <ul class="hx-stats">
          <li><b>{len(POSTS)}+</b><span>bài viết</span></li>
          <li><b>{len(TOPICS)}</b><span>chủ đề</span></li>
          <li><b>{len(steps)}</b><span>chặng lộ trình</span></li>
          <li><b>0đ</b><span>học phí</span></li>
        </ul>
      </div>
      {vision_mock()}
    </div>
  </section>

  <section class="stack" aria-label="Công cụ sẽ học">
    <div class="container stack-inner"><p>Công cụ bạn sẽ thành thạo</p><ul>{stack}</ul></div>
  </section>

  <section class="sec" aria-labelledby="flow-t">
    <div class="container">
      {sec_head("Cách học trên HọcFree", "Học → Thực hành → Trở thành kỹ sư", "Ba bước rõ ràng, đi từ kiến thức đến công việc thật.", center=True, hid="flow-t")}
      <ol class="flow">{flow}</ol>
    </div>
  </section>

  <section class="container" aria-labelledby="path-t">
    <div class="showcase">
      <div>
        <p class="eyebrow">⭐ Lộ trình nổi bật</p>
        <h2 id="path-t">{e(flag['label'])}</h2>
        <p class="showcase-sub">{e(flag['tagline'])}. Từ Python đến triển khai hệ thống Vision trong nhà máy.</p>
        <ul class="showcase-facts">
          <li>{icon("layers")}{len(steps)} chặng</li><li>{icon("clock")}{e(flag['duration'])}</li>
          <li>{icon("calendar")}{e(flag['pace'])}</li><li>{icon("shield-check")}Miễn phí</li>
        </ul>
        <a class="btn lg" href="{path_url(flag)}">Xem lộ trình chi tiết{icon("arrow-right")}</a>
      </div>
      <ol class="phase-list">{phases}</ol>
    </div>
  </section>

  <section class="sec" aria-labelledby="topic-t">
    <div class="container">
      {sec_head("Chủ đề", "Chủ đề được học nhiều nhất", more=("Tất cả chủ đề", section_url(SEC['hoc'])), hid="topic-t")}
      <div class="topic-tiles">{tiles}</div>
    </div>
  </section>

  <section class="sec soft" aria-labelledby="new-t">
    <div class="container">
      {sec_head("Mới cập nhật", "Bài viết mới", more=("Xem tất cả bài viết", "search.html"), hid="new-t")}
      <div class="mag">{feature}<div class="mag-list">{items}</div></div>
    </div>
  </section>

  <section class="sec" aria-labelledby="ex-t">
    <div class="container">
      {sec_head("Khám phá", "Không chỉ có lập trình", "Kiến thức nền, tin tức, ngoại ngữ và tài nguyên để học nhanh hơn.", hid="ex-t")}
      <div class="explore">{explore}</div>
    </div>
  </section>

  <section class="container cta-wrap">
    <div class="cta-band">
      <div><h2>Sẵn sàng trở thành Vision Engineer?</h2><p>Bắt đầu từ chặng 1 ngay hôm nay. Miễn phí, không cần đăng ký.</p></div>
      <a class="btn lg" href="{path_url(flag)}#step-{steps[0]['slug']}">Bắt đầu lộ trình{icon("arrow-right")}</a>
    </div>
  </section>
</main>
"""
    page += footer(root)
    write("index.html", page)


# ---------------------------------------------------------------- bài viết
def add_heading_ids(body):
    toc = []

    def repl(m):
        level, inner = m.group(1), m.group(2)
        hid = slugify(strip_tags(inner))
        if level == "2":
            toc.append((hid, strip_tags(inner).strip()))
        return f'<h{level} id="{hid}">{inner}</h{level}>'

    body = re.sub(r"<h([23])>(.*?)</h\1>", repl, body)
    return body, toc


def build_post(p):
    root = "../"
    url = post_url(p)
    body, toc = add_heading_ids(p["body"])
    toc_html = ""
    if len(toc) >= 3:
        # Tiêu đề đã tự đánh số ("1. …") thì bỏ số của danh sách để không bị "1. 1."
        numbered = any(re.match(r"\d+[.)]\s", t) for _, t in toc)
        toc_html = ('<details class="toc" open><summary>Nội dung bài viết</summary>'
                    + ('<ol class="toc-plain">' if numbered else "<ol>")
                    + "".join(f'<li><a href="#{h}">{e(t)}</a></li>' for h, t in toc) + "</ol></details>")
    same = [x for x in POSTS if x["category"] == p["category"] and x["slug"] != p["slug"]]
    others = [x for x in POSTS if x["category"] != p["category"]]
    related = (same + others)[:3]
    idx = POSTS.index(p)
    newer = POSTS[idx - 1] if idx > 0 else None
    older = POSTS[idx + 1] if idx + 1 < len(POSTS) else None
    pager = '<nav class="pager" aria-label="Bài trước/sau">'
    pager += (f'<a class="prev" href="{root}{post_url(older)}"><span>← Bài trước</span>{e(older["title"])}</a>'
              if older else "<span></span>")
    pager += (f'<a class="next" href="{root}{post_url(newer)}"><span>Bài tiếp →</span>{e(newer["title"])}</a>'
              if newer else "<span></span>")
    pager += "</nav>"
    tags = "".join(f'<a class="tag" href="{root}search.html?q={e(t)}">#{e(t)}</a>' for t in p["tags"])
    share_url = f"{SITE['domain']}/{url}"
    share = f"""<div class="share">
      <span>Chia sẻ:</span>
      <a class="share-btn fb" href="https://www.facebook.com/sharer/sharer.php?u={share_url}" target="_blank" rel="noopener" aria-label="Chia sẻ Facebook">{ICON['fb']}</a>
      <a class="share-btn x" href="https://twitter.com/intent/tweet?url={share_url}" target="_blank" rel="noopener" aria-label="Chia sẻ X">{ICON['x']}</a>
      <button class="share-btn copy-link" data-url="{share_url}" aria-label="Sao chép liên kết">{ICON['link']}</button>
    </div>"""
    article_ld = {
        "@context": "https://schema.org", "@type": "Article", "headline": p["title"], "description": p["excerpt"],
        "image": [f"{SITE['domain']}/{og_img(p)}"], "datePublished": p["date"], "dateModified": p.get("updated", p["date"]),
        "inLanguage": "vi", "articleSection": p["cat"]["name"], "keywords": ", ".join(p["tags"]),
        "wordCount": len(strip_tags(p["body"]).split()),
        "author": {"@type": "Organization", "name": SITE["author"], "url": f"{SITE['domain']}/gioi-thieu.html"},
        "publisher": ORG, "mainEntityOfPage": {"@type": "WebPage", "@id": share_url}}
    crumb_ld = breadcrumb_ld([(p["cat"]["name"], f"{p['category']}/"), (p["title"], None)])
    og_extra = (f'<meta property="article:published_time" content="{p["date"]}">\n'
                f'<meta property="article:section" content="{e(p["cat"]["name"])}">\n'
                + "".join(f'<meta property="article:tag" content="{e(t)}">\n' for t in p["tags"]))
    extra = og_extra + ld_json(article_ld, crumb_ld)

    page = head(root, p["title"], p["excerpt"], url, og_img(p), og_type="article", extra=extra)
    page += header(root, active=p["cat"]["section"])
    page += f"""<main id="main">
  <div class="container layout article-layout">
    <article class="article">
      <nav class="breadcrumb" aria-label="Breadcrumb"><a href="{link(root)}">Trang chủ</a><span>/</span><a href="{root}{p['category']}/">{e(p['cat']['name'])}</a></nav>
      <header class="article-head">
        {cat_pill(root, p)}
        <h1>{e(p['title'])}</h1>
        <p class="lead">{e(p['excerpt'])}</p>
        <div class="article-meta">
          <span class="avatar" aria-hidden="true">HF</span>
          {meta(p, author=True)}
        </div>
      </header>
      <figure class="article-cover">
        <img src="{root}{img_url(p)}" alt="{e(p['title'])}" width="1200" height="675" fetchpriority="high" decoding="async">
      </figure>
      {toc_html}
      <div class="prose">
{body}
      </div>
      <footer class="article-foot">
        <div class="tags">{tags}</div>
        {share}
      </footer>
      <div class="author-box">
        <span class="avatar lg" aria-hidden="true">HF</span>
        <div>
          <strong>{e(SITE['author'])}</strong>
          <p>Chúng tôi viết những bài hướng dẫn dễ hiểu, thực tế để ai cũng có thể tự học lập trình và ngoại ngữ, hoàn toàn miễn phí.</p>
        </div>
      </div>
      {pager}
    </article>
    {sidebar(root, current=p['slug'])}
  </div>
  <section class="band">
    <div class="container">
      {section_title('Có thể bạn quan tâm')}
      <div class="card-grid">{''.join(card(root, r) for r in related)}</div>
    </div>
  </section>
</main>
"""
    page += footer(root)
    write(url, page)


# ---------------------------------------------------------------- trang phụ
def build_search():
    root = ""
    page = head(root, "Tìm kiếm", "Tìm kiếm bài viết trên HọcFree.", "search.html", "assets/images/og-default.jpg",
                robots="noindex, follow")
    page += header(root)
    page += f"""<main id="main">
  <div class="page-head">
    <div class="container">
      <nav class="breadcrumb" aria-label="Breadcrumb"><a href="{link(root)}">Trang chủ</a><span>/</span><span>Tìm kiếm</span></nav>
      <h1>Tìm kiếm</h1>
      <form class="search-form big" action="search.html" role="search">
        {ICON['search']}
        <input type="search" name="q" id="search-page-input" placeholder="Nhập từ khóa…" aria-label="Từ khóa tìm kiếm">
        <button class="btn" type="submit">Tìm</button>
      </form>
    </div>
  </div>
  <div class="container layout">
    <div class="content">
      <p class="search-summary" id="search-summary"></p>
      <div class="post-list" id="search-results"></div>
    </div>
    {sidebar(root)}
  </div>
</main>
"""
    page += footer(root)
    write("search.html", page)


def build_about():
    root = ""
    counts = "".join(
        f'<li><a href="{section_url(s)}"><strong>{e(s["label"])}</strong></a>: {e(s["description"])}</li>'
        for s in SECTIONS if s.get("description"))
    page = head(root, "Giới thiệu", "Giới thiệu về HọcFree.vn – website chia sẻ kiến thức miễn phí.",
                "gioi-thieu.html", "assets/images/og-default.jpg")
    page += header(root)
    page += f"""<main id="main">
  <div class="container layout article-layout">
    <article class="article">
      <nav class="breadcrumb" aria-label="Breadcrumb"><a href="{link(root)}">Trang chủ</a><span>/</span><span>Giới thiệu</span></nav>
      <header class="article-head"><h1>Về HọcFree</h1>
      <p class="lead">Kiến thức là để chia sẻ. HọcFree ra đời với mong muốn ai cũng có thể tự học AI, lập trình, Computer Vision và ngoại ngữ mà không phải lo về chi phí.</p></header>
      <div class="prose">
        <h2>Chúng tôi viết về điều gì?</h2>
        <ul>{counts}</ul>
        <h2>Nguyên tắc</h2>
        <ul>
          <li><strong>Miễn phí mãi mãi</strong>: mọi bài viết đều đọc được mà không cần đăng ký.</li>
          <li><strong>Dễ hiểu</strong>: giải thích bằng tiếng Việt, ví dụ thực tế, có thể làm theo ngay.</li>
          <li><strong>Chính xác</strong>: nội dung được kiểm tra và cập nhật thường xuyên.</li>
        </ul>
        <h2>Công nghệ</h2>
        <p>Website được xây dựng hoàn toàn bằng HTML, CSS và JavaScript thuần, lưu trữ miễn phí trên GitHub Pages. </p>
      </div>
    </article>
    {sidebar(root)}
  </div>
</main>
"""
    page += footer(root)
    write("gioi-thieu.html", page)


def build_404():
    # Trang 404 được GitHub Pages trả về ở mọi đường dẫn, nên dùng đường dẫn tuyệt đối
    root = "/"
    page = head(root, "Không tìm thấy trang", "Trang bạn tìm không tồn tại.", "404.html", "assets/images/og-default.jpg",
                robots="noindex, follow")
    page += header(root)
    page += f"""<main id="main">
  <div class="container notfound">
    <p class="big-404">404</p>
    <h1>Ối, trang này không tồn tại</h1>
    <p>Có thể đường dẫn đã bị thay đổi hoặc bài viết đã được chuyển đi. Hãy thử tìm kiếm nhé.</p>
    <form class="search-form big" action="/search.html" role="search">
      {ICON['search']}
      <input type="search" name="q" placeholder="Nhập từ khóa…" aria-label="Từ khóa tìm kiếm">
      <button class="btn" type="submit">Tìm</button>
    </form>
    <a class="btn ghost" href="/">← Về trang chủ</a>
  </div>
</main>
"""
    page += footer(root)
    write("404.html", page)


# ---------------------------------------------------------------- chủ đề & hub
def count_label(n):
    return f"{n} bài" if n else "Sắp có"


def page_head(root, crumbs, title, desc, kicker="", count=""):
    trail = f'<a href="{link(root)}">Trang chủ</a>'
    for label, href in crumbs:
        trail += f'<span>/</span><a href="{root}{href}">{e(label)}</a>' if href else f"<span>/</span><span>{e(label)}</span>"
    kick = f'<p class="page-kicker">{kicker}</p>' if kicker else ""
    cnt = f'<span class="page-count">{count}</span>' if count else ""
    return f"""<div class="page-head">
    <div class="container">
      <nav class="breadcrumb" aria-label="Breadcrumb">{trail}</nav>
      {kick}
      <h1>{e(title)}</h1>
      <p>{e(desc)}</p>
      {cnt}
    </div>
  </div>"""


def auto_desc(label, ps, prefix="", limit=160):
    """Meta description riêng cho từng trang chủ đề: (mô tả) + số bài + tên vài bài tiêu biểu."""
    if not ps:
        return f"Chủ đề {label} trên HọcFree: nội dung đang được biên soạn, xem vị trí của chủ đề trong lộ trình học."
    out = f"{prefix}{len(ps)} bài viết về {label}: "
    for i, p in enumerate(ps):
        add = ("" if i == 0 else "; ") + p["title"]
        if len(out) + len(add) > limit - 1:
            break
        out += add
    return out.rstrip("; :") + "."


def collection_ld(name, desc, url, ps):
    return {"@context": "https://schema.org", "@type": "CollectionPage", "name": name, "description": desc,
            "url": f"{SITE['domain']}/{url}", "inLanguage": "vi", "isPartOf": {"@type": "WebSite", "name": SITE["name"], "url": SITE["domain"] + "/"},
            "mainEntity": {"@type": "ItemList", "numberOfItems": len(ps), "itemListElement": [
                {"@type": "ListItem", "position": i, "url": f"{SITE['domain']}/{post_url(p)}"} for i, p in enumerate(ps[:20], 1)]}}


def step_kicker(sec):
    return f'Bước {sec["step"]} · {e(sec["stepLabel"])}' if sec.get("step") else ""


def build_topic(t):
    root = "../"
    sec, group, item, ps = t["sec"], t["group"], t["item"], t["posts"]
    label = item["label"]
    desc = item.get("desc") or f"Bài học và bài viết về {label} trên HọcFree."
    crumbs = [(sec["label"], section_url(sec))]
    if len(sec["groups"]) > 1:  # mục chỉ có một nhóm thì trang mục không có anchor nhóm
        crumbs.append((group["label"], f"{section_url(sec)}#{group['slug']}"))
    crumbs.append((label, None))

    if ps:
        content = section_title(f"Bài viết về {label}") + f'<div class="post-list">{"".join(post_row(root, p) for p in ps)}</div>'
    else:
        paths = TOPIC_IN_PATH.get(t["ref"], [])
        go = (f'<a class="btn" href="{root}{path_url(paths[0][0])}#step-{paths[0][2]["slug"]}">Xem chặng này trong lộ trình</a>'
              if paths else f'<a class="btn" href="{root}lo-trinh/">Chọn lộ trình học</a>')
        content = f"""<div class="empty-state">
        <h2>Nội dung đang được biên soạn</h2>
        <p>Chủ đề <strong>{e(label)}</strong> đã có chỗ trong chương trình học của HọcFree, bài học sẽ được cập nhật sớm.
        Trong lúc chờ, bạn có thể xem chủ đề này nằm ở đâu trong lộ trình hoặc tìm bài liên quan.</p>
        <div class="empty-actions">{go}<a class="btn ghost" href="{root}search.html?q={e(label)}">Tìm “{e(label)}”</a></div>
      </div>"""

    siblings = "".join(
        f'<li><a href="{root}{TOPIC_BY[sec["slug"] + "/" + i["slug"]]["url"]}"'
        + (' aria-current="page"' if i is item else "")
        + f'><span>{e(i["label"])}</span><span class="count">{count_label(len(TOPIC_BY[sec["slug"] + "/" + i["slug"]]["posts"]))}</span></a></li>'
        for i in group["items"])
    in_paths = "".join(
        f'<a class="path-mini" href="{root}{path_url(p)}#step-{st["slug"]}"><span class="path-mini-k">⭐ {e(p["label"])}</span>'
        f'<span>Chặng {n}: {e(st["title"])}</span></a>'
        for p, n, st in TOPIC_IN_PATH.get(t["ref"], []))
    path_widget = (f'<section class="widget"><h2 class="widget-title">Có trong lộ trình</h2>{in_paths}</section>'
                   if in_paths else "")

    head_html = page_head(root, crumbs, label, desc, step_kicker(sec), f"{len(ps)} bài viết" if ps else "Đang biên soạn")
    meta_desc = auto_desc(label, ps, prefix=f'{item["desc"]}. ' if item.get("desc") else "")
    ld = ld_json(collection_ld(f"{label} – {sec['label']}", meta_desc, t["url"], ps), breadcrumb_ld(
        [(c, h) for c, h in crumbs[:-1] if h and "#" not in h] + [(label, None)]))
    page = head(root, f"{label} – {sec['label']}", meta_desc, t["url"], og_img(ps[0]) if ps else "assets/images/og-default.jpg",
                robots=None if ps else "noindex, follow", extra=ld)
    page += header(root, active=sec["key"])
    page += f"""<main id="main">
  {head_html}
  <div class="container layout">
    <div class="content">
      {content}
    </div>
    <aside class="sidebar">
      <section class="widget">
        <h2 class="widget-title">{e(group['label'])}</h2>
        <ul class="cat-list topic-list">{siblings}</ul>
      </section>
      {path_widget}
    </aside>
  </div>
</main>
"""
    page += footer(root)
    write(t["url"], page)


def topic_overview(root, sec):
    """Lưới chủ đề của một mục: thẻ chủ đề (1 nhóm) hoặc thẻ theo nhóm (nhiều nhóm)."""
    topics = [t for t in TOPICS if t["sec"] is sec]
    groups = sec["groups"]
    if len(groups) == 1:
        cards = "".join(
            f'<a class="topic-card" href="{root}{t["url"]}"><b>{e(t["item"]["label"])}</b>'
            f'<span>{e(t["item"].get("desc", ""))}</span><span class="count">{count_label(len(t["posts"]))}</span></a>'
            for t in topics)
        body = f'<div class="topic-grid">{cards}</div>'
    else:
        body = '<div class="group-grid">'
        for g in groups:
            lis = "".join(
                f'<li><a href="{root}{TOPIC_BY[sec["slug"] + "/" + i["slug"]]["url"]}"><span>{e(i["label"])}</span>'
                f'<span class="count">{count_label(len(TOPIC_BY[sec["slug"] + "/" + i["slug"]]["posts"]))}</span></a></li>'
                for i in g["items"])
            body += f'<section class="group-card" id="{g["slug"]}"><h2>{e(g["label"])}</h2><ul class="cat-list">{lis}</ul></section>'
        body += "</div>"
    return body


def build_hub(sec):
    root = "../"
    topics = [t for t in TOPICS if t["sec"] is sec]
    ps = section_posts(sec)

    body = topic_overview(root, sec)

    feature = ""
    if sec.get("featured"):
        feature = f'<div class="hub-feature">{feature_card(root, PATH_BY[sec["featured"]], big=True)}</div>'
    latest = ""
    if ps:
        latest = section_title("Bài viết mới") + f'<div class="post-list">{"".join(post_row(root, p) for p in ps[:6])}</div>'
    strip = journey(root, sec["key"]) if sec.get("step") else ""

    head_html = page_head(root, [(sec["label"], None)], sec["label"], sec["description"], step_kicker(sec),
                          f"{len(topics)} chủ đề" + (f" · {len(ps)} bài viết" if ps else ""))
    ld = ld_json(collection_ld(sec["label"], sec["description"], f"{sec['slug']}/", ps), breadcrumb_ld([(sec["label"], None)]))
    page = head(root, sec["label"], sec["description"], f"{sec['slug']}/", "assets/images/og-default.jpg", extra=ld)
    page += header(root, active=sec["key"])
    page += f"""<main id="main">
  {head_html}
  <div class="container hub">
    {strip}
    {feature}
    {body}
    {latest}
  </div>
</main>
"""
    page += footer(root)
    write(f"{sec['slug']}/index.html", page)


# ---------------------------------------------------------------- Learning Paths
def build_paths_index():
    root = "../"
    sec = SEC["lo-trinh"]
    flag = next(p for p in PATHS if p.get("flagship"))
    others = "".join(
        f'<article class="path-card" id="{p["slug"]}"><span class="badge-soon">Sắp ra mắt</span>'
        f'<h3>{e(p["label"])}</h3><p class="path-card-sub">{e(p["tagline"])}</p><p>{e(p["description"])}</p></article>'
        for p in PATHS if not p.get("steps"))
    page = head(root, "Learning Paths – Lộ trình học", sec["description"], "lo-trinh/", "assets/images/og-default.jpg",
                extra=ld_json(breadcrumb_ld([("Learning Paths", None)])))
    page += header(root, active="lo-trinh")
    page += f"""<main id="main">
  {page_head(root, [('Learning Paths', None)], 'Learning Paths', sec['description'], step_kicker(sec))}
  <div class="container hub">
    {journey(root, 'lo-trinh')}
    <div class="hub-feature">{feature_card(root, flag, big=True)}</div>
    {section_title('Lộ trình khác')}
    <div class="path-grid">{others}</div>
  </div>
</main>
"""
    page += footer(root)
    write("lo-trinh/index.html", page)


def build_path(p):
    root = "../"
    steps, phases = p["steps"], p["phases"]
    num = {st["slug"]: n for n, st in enumerate(steps, 1)}
    weeks = sum(st["weeks"] for st in steps)

    entries = "".join(
        f'<a class="entry-card" href="#step-{x["step"]}"><b>{e(x["label"])}</b><small>{e(x["detail"])}</small>'
        f'<span>Bắt đầu từ chặng {num[x["step"]]}: {e(steps[num[x["step"]] - 1]["title"])} →</span></a>'
        for x in p["entryPoints"])

    def topic_chips(st):
        out = ""
        for ref in st["topics"]:
            t = TOPIC_BY[ref]
            out += f'<a class="chip" href="{root}{t["url"]}">{e(t["item"]["label"])}<small>{count_label(len(t["posts"]))}</small></a>'
        return out

    map_html, main_html = "", ""
    for pn, ph in enumerate(phases, 1):
        ph_steps = [st for st in steps if st["phase"] == ph["slug"]]
        map_html += (f'<li><a class="map-phase" href="#gd-{ph["slug"]}">Giai đoạn {pn} · {e(ph["label"])}</a><ol>'
                     + "".join(f'<li><a href="#step-{st["slug"]}" data-map-step="{st["slug"]}"><span class="map-dot" aria-hidden="true"></span>'
                               f'<span>{num[st["slug"]]}. {e(st["title"])}</span></a></li>' for st in ph_steps)
                     + "</ol></li>")
        cards = ""
        for st in ph_steps:
            n = num[st["slug"]]
            learn = "".join(f"<li>{e(x)}</li>" for x in st["learn"])
            cards += f"""<li class="step" id="step-{st['slug']}" data-step="{st['slug']}">
          <span class="step-marker" aria-hidden="true">{n}</span>
          <div class="step-card">
            <div class="step-head">
              <h3><span class="sr-only">Chặng {n}: </span>{e(st['title'])}</h3>
              <span class="step-here">Bạn đang ở đây</span>
              <span class="step-weeks">~{st['weeks']} tuần</span>
            </div>
            <div class="step-cols">
              <div><p class="step-label">Bạn sẽ học</p><ul>{learn}</ul></div>
              <div class="step-outcome"><p class="step-label">Học xong bạn có thể</p><p>{e(st['outcome'])}</p></div>
            </div>
            <div class="step-foot">
              <div class="chips">{topic_chips(st)}</div>
              <label class="step-check"><input type="checkbox" data-step-check="{st['slug']}"> Đã hoàn thành</label>
            </div>
          </div>
        </li>"""
        main_html += f"""<section class="phase" id="gd-{ph['slug']}" aria-labelledby="gd-{ph['slug']}-t">
        <h2 class="phase-title" id="gd-{ph['slug']}-t"><span>Giai đoạn {pn}</span>{e(ph['label'])}</h2>
        <ol class="steps">{cards}</ol>
      </section>"""

    g = p["goal"]
    can = "".join(f"<li>{e(x)}</li>" for x in g["can"])
    roles = "".join(f"<li>{e(x)}</li>" for x in g["roles"])
    first = steps[0]
    ld = json.dumps({
        "@context": "https://schema.org", "@type": "Course", "name": p["label"], "description": p["description"],
        "provider": {"@type": "Organization", "name": SITE["name"], "sameAs": SITE["domain"]},
        "isAccessibleForFree": True, "inLanguage": "vi",
        "hasPart": [{"@type": "Course", "name": st["title"], "description": st["outcome"]} for st in steps],
    }, ensure_ascii=False)

    page = head(root, p["label"], p["description"], path_url(p), "assets/images/og-default.jpg",
                extra=f'<script type="application/ld+json">{ld}</script>\n'
                + ld_json(breadcrumb_ld([("Learning Paths", "lo-trinh/"), (p["label"], None)])))
    page += header(root, active="lo-trinh")
    page += f"""<main id="main" class="path-page" data-path="{p['slug']}">
  <div class="page-head path-head">
    <div class="container">
      <nav class="breadcrumb" aria-label="Breadcrumb"><a href="{link(root)}">Trang chủ</a><span>/</span><a href="{root}lo-trinh/">Learning Paths</a><span>/</span><span>{e(p['short'])}</span></nav>
      <p class="page-kicker">⭐ Learning Path flagship</p>
      <h1>{e(p['label'])}</h1>
      <p class="path-tagline">{e(p['tagline'])}</p>
      <p>{e(p['description'])}</p>
      <ul class="path-stats">
        <li><b>{len(steps)}</b> chặng</li>
        <li><b>{len(phases)}</b> giai đoạn</li>
        <li><b>{e(p['duration'])}</b> {e(p['pace'])} · ~{weeks} tuần</li>
        <li><b>Miễn phí</b></li>
      </ul>
      <div class="path-actions">
        <a class="btn" href="#step-{first['slug']}" data-path-continue>Bắt đầu chặng 1: {e(first['title'])}</a>
        <a class="btn ghost-light" href="#muc-tieu">Xem đích đến</a>
      </div>
    </div>
  </div>

  <section class="container path-where" aria-labelledby="where-t">
    <h2 class="path-h2" id="where-t">Bạn đang ở đâu?</h2>
    <p class="muted">Chọn điểm xuất phát phù hợp, không cần học lại những gì đã biết.</p>
    <div class="entry-grid">{entries}</div>
  </section>

  <div class="container path-layout">
    <aside class="path-map" aria-label="Bản đồ lộ trình">
      <div class="path-progress">
        <div class="path-progress-head"><b>Tiến độ của bạn</b><span data-progress-text>0/{len(steps)} chặng</span></div>
        <div class="path-bar"><span data-progress-bar></span></div>
      </div>
      <ol class="map-phases">{map_html}</ol>
      <a class="map-goal" href="#muc-tieu">🎯 {e(g['title'])}</a>
      <p class="path-note">Đánh dấu “Đã hoàn thành” ở mỗi chặng; tiến độ được lưu trên trình duyệt này.</p>
    </aside>
    <div class="path-main">
      {main_html}
      <section class="goal" id="muc-tieu" aria-labelledby="goal-t">
        <span class="step-marker goal-marker" aria-hidden="true">🎯</span>
        <div class="goal-card">
          <p class="page-kicker">Đích đến</p>
          <h2 id="goal-t">{e(g['title'])}</h2>
          <p>{e(g['summary'])}</p>
          <div class="step-cols">
            <div><p class="step-label">Bạn có thể làm</p><ul>{can}</ul></div>
            <div><p class="step-label">Vị trí có thể ứng tuyển</p><ul class="role-list">{roles}</ul></div>
          </div>
        </div>
      </section>
    </div>
  </div>
</main>
"""
    page += footer(root)
    write(path_url(p), page)


def build_login():
    root = ""
    page = head(root, "Đăng nhập", "Tài khoản HọcFree.", "dang-nhap.html", "assets/images/og-default.jpg",
                robots="noindex, follow")
    page += header(root)
    page += f"""<main id="main">
  <div class="container notfound">
    <h1>Tài khoản HọcFree sắp ra mắt</h1>
    <p>Hiện tại mọi bài học đều mở miễn phí, không cần đăng nhập. Tiến độ Learning Path được lưu ngay trên trình duyệt của bạn.</p>
    <a class="btn" href="{root}lo-trinh/">Bắt đầu học</a>
  </div>
</main>
"""
    page += footer(root)
    write("dang-nhap.html", page)


def build_search_data():
    items = [{
        "t": p["title"], "u": post_url(p), "e": p["excerpt"], "c": p["category"], "cn": p["cat"]["name"],
        "d": fmt_date(p["date"]), "m": p["minutes"], "img": img_url(p), "tags": p["tags"],
    } for p in POSTS]
    # Chủ đề & lộ trình cũng tìm được, kể cả khi chưa có bài
    topics = [{
        "t": t["item"]["label"], "u": t["url"], "s": t["sec"]["label"],
        "g": t["group"]["label"] if t["group"]["label"] != t["sec"]["label"] else "", "n": len(t["posts"]),
    } for t in TOPICS]
    topics += [{"t": p["label"], "u": path_url(p), "s": "Learning Path", "g": p["tagline"], "n": -1,
                "f": 1 if p.get("flagship") else 0} for p in PATHS]
    write("assets/js/search-data.js",
          "/* Tự động sinh bởi tools/build.py – không sửa tay */\nwindow.HF_POSTS = "
          + json.dumps(items, ensure_ascii=False, indent=1) + ";\nwindow.HF_TOPICS = "
          + json.dumps(topics, ensure_ascii=False, indent=1) + ";\n")


def build_sitemap():
    today = date.today().isoformat()
    urls = [("", today, "1.0")] + [(f"{s['slug']}/", today, "0.8") for s in SECTIONS if s.get("groups")]
    urls += [("lo-trinh/", today, "0.8")] + [(path_url(p), today, "0.9") for p in PATHS if p.get("steps")]
    urls += [(t["url"], today, "0.6") for t in TOPICS if t["posts"]]  # chủ đề trống để noindex
    urls += [(post_url(p), p["date"], "0.7") for p in POSTS] + [("gioi-thieu.html", today, "0.3")]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += "".join(f"  <url><loc>{SITE['domain']}/{u}</loc><lastmod>{d}</lastmod><priority>{pr}</priority></url>\n"
                   for u, d, pr in urls)
    xml += "</urlset>\n"
    write("sitemap.xml", xml)
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE['domain']}/sitemap.xml\n")


def main():
    build_home()
    for p in POSTS:
        build_post(p)
    for s in SECTIONS:
        if s.get("groups"):
            build_hub(s)
    for t in TOPICS:
        if not t["item"].get("href"):
            build_topic(t)
    build_paths_index()
    for p in PATHS:
        if p.get("steps"):
            build_path(p)
    build_search()
    build_about()
    build_404()
    build_login()
    build_search_data()
    build_sitemap()
    print(f"Xong: {len(POSTS)} bài viết, {len(TOPICS)} chủ đề, "
          f"{sum(1 for p in PATHS if p.get('steps'))} lộ trình.")


if __name__ == "__main__":
    main()
