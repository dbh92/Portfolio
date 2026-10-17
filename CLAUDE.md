# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

HọcFree (hocfree.vn): a static, Vietnamese-language learning site (AI, Computer Vision, Machine Vision, programming, languages) served by GitHub Pages from the repo root of `main` (`CNAME`, `.nojekyll`). Plain HTML/CSS/JS, no bundler, no npm. A single Python script generates every page from JSON + HTML fragments in `src/`.

All site content, commit messages and code comments are in Vietnamese with full diacritics. Keep it that way.

## Commands

```bash
python tools/make_thumbs.py        # draw missing post thumbnails (needs Pillow); --all redraws everything
python tools/build.py              # regenerate all HTML, search index, sitemap, robots.txt
python tools/check_site.py         # validator; must print "OK: không có lỗi" (exit 1 on errors)
python -m http.server 8000         # preview at http://localhost:8000
```

There is no test suite; `check_site.py` is the test. Run it after every build. It checks internal links and `#anchors`, exactly one `<h1>` per page, title/description/canonical, JSON-LD parses, post bodies have balanced tags and no `<h1>`, `<`/`&` are escaped inside `<pre><code>`, Python code blocks parse with `ast`, and every post has a body file plus `.jpg` and `.webp` thumbnails.

## Generated vs. source files

**Never hand-edit generated output.** Edit the source in `src/` (or `tools/build.py`, `assets/`), then rebuild:

- Generated: every `.html` at the root and in `hoc/ projects/ lo-trinh/ kien-thuc/ tin-tuc-ai/ ngoai-ngu/ tai-nguyen/`, plus `assets/js/search-data.js`, `sitemap.xml`, `robots.txt`.
- Hand-written: `src/*.json`, `src/posts/<slug>.html`, `tools/*.py`, `assets/css/*`, `assets/js/main.js`.
- Commit generated files together with their sources; GitHub Pages serves them directly.
- `build.py` stamps `?v=YYYYMMDD` (today's date) on CSS/JS URLs, so a rebuild on a new day touches every page. That diff is expected.

## Data model (how `build.py` wires things)

- **`src/posts.json`**: `site` metadata, `downloads` (Google Drive links, inserted into bodies via `{{download:<key>}}`; `ready: false` adds a "not uploaded yet" note), `popular` (slugs for the "most read" widget), and `posts`. Keep **one post per line** in `posts`; when editing programmatically, use Python and `json.dumps(..., ensure_ascii=False)` per entry. Post fields: `slug, category, title, excerpt, date, tags, thumb{glyph, colors[light, dark]}`, optional `math: true` (loads self-hosted KaTeX from `assets/vendor/katex`; write `\( … \)` inline and `\[ … \]` for display).
- **`category`** must be a `nav.json` section that has `groups` (`hoc, projects, kien-thuc, tin-tuc-ai, ngoai-ngu, tai-nguyen`). The page is written to `<category>/<slug>.html`.
- **`src/nav.json`**: sections → groups → topic items. The menu holds topics only, never posts. A topic page `<section>/<topic>.html` lists every post whose `tags` match the topic's `tags` (case-insensitive), optionally limited by `categories`. So **tags decide which topic pages a post shows up on**. A topic with no posts renders as "Đang biên soạn" with `noindex` and stays out of the sitemap. Topic slugs must not collide with post slugs (enforced by an assert).
- **`src/learning-paths.json`**: career paths (the flagship is `vision-engineer`: phases → 14 steps). Each step has `topics` (refs like `hoc/opencv`, which must exist in nav.json), ordered `lessons` (`slug, kind: lesson|lab|project, min, title, goals, practice?`) and `extras` (supplementary-reading slugs, which must exist in posts.json). A lesson whose slug exists in posts.json is published as a full lesson page: course bar, goals, practice, prev/next across steps, "mark done" button. A slug without a post shows as "Đang biên soạn". A post can be a lesson in only one step. Pages: `lo-trinh/<path>.html` and `lo-trinh/<path>/<step>.html`.
- **`src/posts/<slug>.html`**: body fragment only (no `<html>/<head>/<h1>`, no inline styles or scripts). Uses `<h2>/<h3>/<p>/<ul>/<table>/<pre><code>`. `<h2>`/`<h3>` get auto ids, and three or more `<h2>` produce a TOC. Link to other posts with `slug.html` within the same category, or `../<category>/slug.html` across categories. Reading time is computed at ~180 words/min.
- **`src/icons.json`**: Lucide SVG inner markup, used through `icon("name")` in `build.py`.
- **Thumbnails**: `assets/images/posts/<slug>.webp` is shown on the site and `<slug>.jpg` is used for og:image. Drop in a real `.jpg` and `make_thumbs.py` derives the `.webp` without overwriting it.
- `build.py` validates its inputs with `assert`s at import time, so a bad reference fails the build before anything is written.

## Client-side JS (`assets/js/main.js`)

A single IIFE that handles dark mode (`localStorage` key `hf-theme`), the mega menu and mobile drawer, search (`Ctrl K` or `/`, over `window.HF_POSTS` and topics from `search-data.js`), copy-code buttons, and learning-path/lesson progress stored in `localStorage`. No framework.

## Automated daily publishing

`docs/auto-publish.md` is the spec for a scheduled Claude Code routine that publishes 10 posts per day, driven by `src/editorial-plan.json`: `topics` maps refs to category/tags, and `days[]` holds `date`, `topics`, `status: pending|published` and `posts`. When running as that routine, follow that file exactly, including its restriction to touching only `src/posts.json`, `src/posts/*.html`, `src/editorial-plan.json`, thumbnails and generated HTML, and never editing or deleting existing posts. Its content rules apply to any new post: verify facts and API names with web search, never invent numbers or sources, cover only real events from roughly the last 10 days in `tin-tuc-ai`, make code runnable, keep bodies at about 700–1500 words, titles at 70 characters or fewer, excerpts at 120–170 characters, and end with a `<p class="note">Nguồn tham khảo: …</p>` when external facts are used.
