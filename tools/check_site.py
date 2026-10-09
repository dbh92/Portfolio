"""Kiểm tra site sau khi build. Thoát với mã 1 nếu có lỗi.

Chạy:  python tools/check_site.py

Kiểm tra:
- Link nội bộ (href/src) trỏ tới file có thật, anchor #id tồn tại.
- Thân bài viết (src/posts/*.html): thẻ HTML đóng mở cân bằng, không có <h1>,
  ký tự < và & trong <pre><code> đã escape, khối code Python không lỗi cú pháp.
- Mỗi trang: đúng 1 thẻ h1, có title, description, canonical; JSON-LD parse được.
- Mỗi bài trong src/posts.json có file thân bài và ảnh đại diện (.jpg + .webp).
"""
import ast
import glob
import html
import json
import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
errors = []


def err(*a):
    errors.append(" ".join(str(x) for x in a))


# ---------- trang đã build
pages = [p for p in glob.glob("**/*.html", recursive=True) if not p.startswith(("src/", "tools/", "node_modules/"))]
ids_cache = {}


def ids(f):
    if f not in ids_cache:
        ids_cache[f] = set(re.findall(r'\sid="([^"]+)"', open(f, encoding="utf-8").read()))
    return ids_cache[f]


for p in pages:
    t = open(p, encoding="utf-8").read()
    for u in re.findall(r'(?:href|src)="([^"]+)"', t):
        if u.startswith(("http", "mailto:", "tel:", "data:", "javascript:", "#")):
            continue
        path, _, frag = u.partition("#")
        path = path.split("?")[0]
        if path.startswith("/"):
            tgt = os.path.normpath("." + unquote(path))
        elif path:
            tgt = os.path.normpath(os.path.join(os.path.dirname(p), unquote(path)))
        else:
            tgt = p
        if path.endswith("/") or os.path.isdir(tgt):
            tgt = os.path.join(tgt, "index.html")
        if not os.path.exists(tgt):
            err("link hỏng:", p, "→", u)
        elif frag and tgt.endswith(".html") and frag not in ids(tgt):
            err("anchor hỏng:", p, "→", u)
    if 'http-equiv="refresh"' in t:  # trang chuyển hướng: không cần SEO
        continue
    if len(re.findall(r"<h1[\s>]", t)) != 1:
        err("số h1 khác 1:", p)
    for tag in (r"<title>", r'<meta name="description"', r'<link rel="canonical"'):
        if not re.search(tag, t):
            err("thiếu", tag, "trong", p)
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try:
            json.loads(blk)
        except ValueError as ex:
            err("JSON-LD lỗi:", p, ex)

# ---------- thân bài viết
VOID = {"br", "img", "hr", "input", "meta", "link", "source", "wbr", "col", "area", "base", "embed", "track", "param"}


class Balance(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.bad = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            self.bad.append(tag)


py_blocks = 0
for f in sorted(glob.glob("src/posts/*.html")):
    t = open(f, encoding="utf-8").read()
    b = Balance()
    b.feed(t)
    b.close()
    if b.bad or b.stack:
        err("thẻ HTML không cân bằng:", f, b.bad[:3], b.stack[-3:])
    if re.search(r"<h1\b", t):
        err("thân bài không được có <h1>:", f)
    for blk in re.findall(r"<pre><code[^>]*>(.*?)</code></pre>", t, re.S):
        if re.search(r"<(?!/?(span|b|i|em|strong)\b)", blk):
            err("ký tự < chưa escape trong <pre><code>:", f, blk[:50].replace("\n", " "))
        if re.search(r"&(?!(lt|gt|amp|quot|#\d+|#x[0-9a-fA-F]+|nbsp|apos);)", blk):
            err("ký tự & chưa escape trong <pre><code>:", f)
        code = html.unescape(re.sub(r"<[^>]+>", "", blk))
        looks_py = re.search(r"^(import |from \w+ import|def |for .* in .*:$)", code, re.M)
        other = re.search(r"^\s*(using |public |var |\$ |pip |git |docker |FROM |RUN )", code, re.M)
        if "(minh họa)" in code:  # khối cố ý chứa lỗi để người học tự sửa
            continue
        if looks_py and not other:
            py_blocks += 1
            try:
                ast.parse(code)
            except SyntaxError as ex:
                err("code Python lỗi cú pháp:", f, f"dòng {ex.lineno}: {ex.msg}")

# ---------- dữ liệu bài viết
data = json.load(open("src/posts.json", encoding="utf-8"))
slugs = [p["slug"] for p in data["posts"]]
if len(slugs) != len(set(slugs)):
    err("slug bài viết bị trùng")
for p in data["posts"]:
    for path in (f"src/posts/{p['slug']}.html", f"assets/images/posts/{p['slug']}.jpg", f"assets/images/posts/{p['slug']}.webp"):
        if not os.path.exists(path):
            err("thiếu file:", path)

print(f"{len(pages)} trang, {len(slugs)} bài, {py_blocks} khối code Python")
if errors:
    print(f"\n{len(errors)} LỖI:")
    for e in errors[:80]:
        print(" -", e)
    sys.exit(1)
print("OK: không có lỗi")
