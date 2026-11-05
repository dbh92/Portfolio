# 06. Bên trong `tools/build.py`

Tài liệu cho người sửa trình sinh trang. `build.py` khoảng 1.600 dòng Python thuần, không thư viện ngoài,
không template engine: mỗi trang là một f-string lớn ghép từ các hàm nhỏ.

## Thứ tự thực thi

### 1. Nạp và chuẩn bị dữ liệu (chạy ngay khi import)

| Bước | Biến tạo ra |
|---|---|
| Đọc `src/posts.json` | `DATA`, `SITE`, `DOWNLOADS` |
| Sắp bài theo `date` giảm dần | `POSTS` (danh sách), `BY_SLUG` (slug → bài) |
| Đọc `src/nav.json`, `src/learning-paths.json` | `NAV`, `SECTIONS`, `SEC` (key → mục), `JOURNEY` (mục có `step`, theo thứ tự), `PATHS`, `PATH_BY` |
| Xác định chuyên mục | `CATS`: mọi mục có `groups`, khóa là `slug` |
| Với mỗi bài: đọc thân bài, thay `{{download:…}}`, đếm từ | `p["body"]`, `p["minutes"]`, `p["cat"]` |
| Dựng danh sách chủ đề, gom bài theo tag | `TOPICS`, `TOPIC_BY` (ref → chủ đề) |
| Chủ đề → các chặng nhắc tới nó | `TOPIC_IN_PATH` |
| Bài viết là bài học của chặng nào | `LESSON` (slug → `{path, n, step, i, lesson}`) |
| Đọc `src/icons.json` | `ICONS` |

`VERSION = date.today().strftime("%Y%m%d")` dùng cho `?v=` trên CSS/JS.

### 2. `main()` ghi trang

```
build_home()
build_post(p)          cho mọi bài
build_hub(s)           cho mọi mục có groups
build_topic(t)         cho mọi chủ đề không có href
build_paths_index()
build_path(p)          cho mọi lộ trình có steps
  build_step(p, n, st) cho mọi chặng
  lo-trinh/<path>/index.html (chuyển hướng)
build_search(), build_about(), build_404(), build_login()
build_search_data()    assets/js/search-data.js
build_sitemap()        sitemap.xml, robots.txt
```

Mọi file ghi qua `write(rel, content)`: tạo thư mục nếu thiếu, UTF-8, xuống dòng `\n`, in `ghi <đường dẫn>`.

**Build không xóa file.** Trang của bài, chủ đề, chặng đã bị xóa hoặc đổi slug vẫn nằm lại trên đĩa; phải
`git rm` bằng tay.

## Các kiểm tra khi nạp dữ liệu

Chạy trước khi ghi bất kỳ file nào:

| Thông báo | Nguyên nhân |
|---|---|
| `Bài <slug>: không có downloads.<key> trong posts.json` | Thân bài dùng `{{download:key}}` chưa khai báo |
| `Bài <slug>: category phải là một trong [...]` | `category` không phải slug của một mục có `groups` |
| `Trùng slug chủ đề trong src/nav.json` | Hai chủ đề cùng `slug` trong một mục |
| `Slug chủ đề trùng với slug bài viết` | URL trang chủ đề trùng URL một bài |
| `Lộ trình <slug>: chủ đề <ref> không có trong nav.json` | `topics` của chặng trỏ tới chủ đề không tồn tại |
| `Bài học <slug>: kind phải là [...]` | `kind` khác `lesson`, `lab`, `project` |
| `Bài <slug> nằm trong hai chặng` | Một bài viết được khai là bài học ở hai chặng |
| `Chặng <slug>: bài đọc thêm <x> không có trong posts.json` | `extras` trỏ tới bài không tồn tại |
| `FileNotFoundError: …src/posts/<slug>.html` | Bài trong JSON chưa có thân bài |

Một số dữ liệu sai **không** có `assert` riêng và báo lỗi Python thô, có khi giữa lúc ghi trang (site bị build
dở, chỉ cần sửa rồi build lại):

| Lỗi | Nguyên nhân thường gặp |
|---|---|
| `KeyError: '<slug>'` trong `featured_paths` | `featured` của mục trỏ tới lộ trình không tồn tại |
| `KeyError: '<ref>'` trong `search_dialog` / `build_home` | `popularTopics` trỏ tới chủ đề không tồn tại |
| `KeyError` trong `build_path` | `entryPoints[].step` không phải slug chặng |
| `StopIteration` trong `build_step` | `phase` của chặng không có trong `phases` |
| `StopIteration` trong `build_home` / `search_dialog` | Không có lộ trình nào `flagship: true` |
| `KeyError: '<tên>'` trong `icon()` | Icon chưa có trong `src/icons.json` |
| `KeyError: 'hoc'` (hoặc khóa mục khác) | Đổi `key` của mục mà trang chủ tham chiếu cứng |
| `json.decoder.JSONDecodeError` | JSON sai cú pháp (dấu phẩy thừa, thiếu nháy) |

## Đường dẫn tương đối và `root`

Mọi link trong trang là tương đối để site chạy được ở mọi tên miền và cả khi mở bằng `file://`. Mỗi hàm dựng
trang đặt `root` theo độ sâu của trang:

| Trang | `root` |
|---|---|
| `index.html`, `search.html`, `gioi-thieu.html`, `dang-nhap.html` | `""` |
| `<mục>/…`, `lo-trinh/<path>.html` | `"../"` |
| `lo-trinh/<path>/<step>.html` | `"../../"` |
| `404.html` | `"/"` (GitHub Pages trả trang này ở mọi độ sâu nên phải dùng đường dẫn tuyệt đối) |

`root` được ghi vào `<html data-root="…">` để `main.js` dựng link kết quả tìm kiếm. Hàm `link(root, rel)` trả
`"./"` khi ghép ra chuỗi rỗng (link về trang chủ từ trang chủ).

## Hàm tiện ích

| Hàm | Việc |
|---|---|
| `slugify(text)` | Bỏ dấu tiếng Việt (`đ` → `d`), chữ thường, ký tự khác chữ số thành `-`. Dùng cho id tiêu đề. |
| `fmt_date(iso)` | `2026-10-05` → `05/10/2026` |
| `strip_tags(s)` | Bỏ thẻ HTML (đếm từ, lấy chữ tiêu đề) |
| `post_url(p)`, `img_url(p)`, `og_img(p)` | `<category>/<slug>.html`, ảnh `.webp`, ảnh `.jpg` |
| `section_url(sec)` | URL thư mục của mục (`hoc/`); trang chủ là `""` |
| `path_url(p)`, `step_url(p, st)` | `lo-trinh/<slug>.html` (hoặc `lo-trinh/#<slug>` nếu chưa có chặng), `lo-trinh/<path>/<step>.html` |
| `match_posts(item)` | Bài thuộc một chủ đề: tag giao nhau (không phân biệt hoa thường) và thuộc `categories` nếu có |
| `section_posts(sec)` | Bài thuộc chuyên mục, hoặc khớp một chủ đề của mục |
| `course_order(p)` | Mọi bài học đã viết của lộ trình theo thứ tự |
| `step_hours(st)` | Tổng `min` / 60, làm tròn |
| `count_label(n)` | `"N bài"` hoặc `"Sắp có"` |
| `auto_desc(label, ps, prefix)` | Meta description trang chủ đề: mô tả + số bài + tên vài bài, ≤ 160 ký tự |
| `add_heading_ids(body)` | Gắn `id` cho `<h2>`/`<h3>`, trả về thân bài và danh sách mục lục (chỉ `<h2>`) |
| `e` | `html.escape`. **Mọi dữ liệu từ JSON đều phải qua `e()`** trước khi vào HTML; chỉ thân bài được chèn nguyên. |

## Khung trang và thành phần

| Hàm | Dựng |
|---|---|
| `head(root, title, desc, canonical, image, og_type, extra, robots)` | `<!DOCTYPE>` đến `<body>`: title, meta, canonical, Open Graph, Twitter Card, theme-color, favicon, manifest, preload font, CSS, script đặt dark mode trước khi vẽ (tránh nháy trắng), `extra` (JSON-LD, KaTeX) |
| `header(root, active)` | Thanh tiến độ đọc, header 2 hàng (logo, nút tìm kiếm, dark mode, đăng nhập, "Bắt đầu học" / menu chính), drawer mobile, hộp tìm kiếm |
| `nav_panel(root, sec)` | Panel của một mục menu theo `layout`: `mega`, `paths` hoặc dropdown |
| `search_dialog(root)` | Hộp tìm kiếm `Ctrl K` với chip chủ đề phổ biến và lộ trình flagship |
| `footer(root)` | Chân trang 5 cột, nút lên đầu trang, hai thẻ `<script defer>` |
| `journey(root, current, cls)` | Dải "Học → Thực hành → Trở thành kỹ sư" |
| `feature_card(root, p, big)` | Thẻ lộ trình (mega menu, trang hub) |
| `post_row`, `card` | Bài dạng hàng (có excerpt) và dạng thẻ (lưới) |
| `sidebar(root, current)` | Đọc nhiều nhất, Chuyên mục, Về HọcFree, mây thẻ |
| `page_head(...)`, `section_title(...)`, `sec_head(...)` | Đầu trang hub/chủ đề, tiêu đề khối |
| `lesson_parts(root, p)` | Các khối riêng của trang bài học (xem [05](05-lo-trinh-hoc.md#trang-bài-học)) |
| `vision_mock()`, `_pcb()`, `_box()` | Hình SVG trang trí ở hero trang chủ (băng tải, 3 bo mạch, khung OK/NG). Số liệu trong hình là minh họa. |

## Quy tắc chọn nội dung

| Chỗ | Quy tắc |
|---|---|
| Trang chủ, "Bài viết mới" | 5 bài mới nhất, tối đa 2 bài mỗi chuyên mục; bài đầu là bài lớn |
| Trang chủ, số liệu hero | Số bài, số chủ đề, số chặng của lộ trình flagship |
| Trang hub, "Bài viết mới" | 6 bài mới nhất của `section_posts` |
| Bài viết, "Có thể bạn quan tâm" | 3 bài: ưu tiên cùng chuyên mục, mới nhất trước, rồi bài khác chuyên mục |
| Bài viết, nút trước/sau | Theo ngày: "Bài trước" là bài cũ hơn, "Bài tiếp" là bài mới hơn. Bài học thì theo thứ tự giáo trình. |
| Chân trang, "Bài mới" | 4 bài mới nhất |
| Sidebar, "Đọc nhiều nhất" | 5 slug đầu tiên trong `popular` có tồn tại, bỏ bài đang xem |
| Trang chủ đề | Mọi bài khớp, theo ngày; nếu chủ đề nằm trong một chặng có giáo trình thì theo thứ tự giáo trình trước |

## SEO

### Thẻ `<head>`

- `<title>`: trang chủ là `HọcFree – <tagline>`; trang khác là `<tiêu đề> | HọcFree` nếu tiêu đề ≤ 58 ký tự,
  dài hơn thì chỉ tiêu đề (để Google không cắt mất phần chính).
- `canonical`, `og:url`: URL tuyệt đối từ `site.domain`. Trang hub dùng dạng thư mục (`/hoc/`), trang chủ là `/`.
- `og:image`: ảnh `.jpg` của bài; trang khác dùng `assets/images/og-default.jpg` (trang chủ đề có bài dùng ảnh
  bài đầu tiên). Khai 1200×675.
- Bài viết có thêm `og:type=article`, `article:published_time`, `article:section`, `article:tag`.
- `robots`: mặc định `index, follow, max-image-preview:large`. `noindex, follow` cho `search.html`,
  `dang-nhap.html`, `404.html` và chủ đề chưa có bài. Trang chuyển hướng `lo-trinh/<path>/` là `noindex`.

### JSON-LD

| Trang | Kiểu |
|---|---|
| Trang chủ | `WebSite` (có `SearchAction` tới `search.html?q=`), `Organization` |
| Bài viết | `Article` (+ `isPartOf: Course` nếu là bài học), `BreadcrumbList` |
| Trang hub | `CollectionPage` (tối đa 20 bài trong `ItemList`), `BreadcrumbList` |
| Trang chủ đề | `CollectionPage`, `BreadcrumbList` |
| Trang lộ trình | `Course` (mỗi chặng một `hasPart`), `BreadcrumbList` |
| Trang chặng | `ItemList` (bài học), `BreadcrumbList` |
| `lo-trinh/` | `BreadcrumbList` |

### Sitemap và robots

| URL | `lastmod` | `priority` |
|---|---|---|
| Trang chủ | ngày build | 1.0 |
| Trang lộ trình có chặng | ngày build | 0.9 |
| Trang hub, `lo-trinh/`, trang chặng | ngày build | 0.8 |
| Bài viết | `date` của bài | 0.7 |
| Trang chủ đề **có bài** | ngày build | 0.6 |
| `gioi-thieu.html` | ngày build | 0.3 |

`robots.txt` cho phép mọi thứ và trỏ tới sitemap.

### Chỉ mục tìm kiếm

`build_search_data()` ghi `assets/js/search-data.js`:

- `window.HF_POSTS`: mỗi bài `{t: tiêu đề, u: URL, e: excerpt, c: chuyên mục, cn: tên chuyên mục, d: ngày,
  m: phút đọc, img: ảnh, tags}`.
- `window.HF_TOPICS`: chủ đề `{t, u, s: tên mục, g: tên nhóm, n: số bài}`, lộ trình và chặng (`n: -1`;
  lộ trình flagship có `f: 1`).

File lớn dần theo số bài (khoảng 6.500 dòng với 388 bài) và được tải ở mọi trang. Khi số bài lên hàng nghìn,
cân nhắc bỏ `indent=1` hoặc chỉ tải chỉ mục khi mở hộp tìm kiếm.

## Nội dung viết cứng trong code

Các phần sau nằm trong `build.py`, không trong JSON. Sửa trực tiếp hàm tương ứng:

| Nội dung | Hàm |
|---|---|
| Hero trang chủ (tiêu đề, mô tả, nút), dải "Công cụ bạn sẽ thành thạo", 3 thẻ "Học → Thực hành → Kỹ sư", 4 thẻ "Khám phá", băng CTA cuối | `build_home` (`flow_data`, `explore_data`, `stack`) |
| Icon của chủ đề phổ biến trên trang chủ | `TOPIC_ICON` |
| Trang Giới thiệu (nguyên tắc, công nghệ) | `build_about` |
| Hộp "Về HọcFree" ở sidebar, hộp tác giả cuối bài | `sidebar`, `build_post` |
| Trang Đăng nhập, 404 | `build_login`, `build_404` |
| Logo SVG, icon nhỏ của khung trang | `LOGO`, `ICON` |
| Font được preload | `PRELOAD_FONTS` |

## Mở rộng

### Thêm một trường cho bài viết

1. Thêm trường vào dòng bài trong `posts.json` (trường tùy chọn đọc bằng `p.get("ten", mặc_định)`).
2. Dùng trong `build_post` (hoặc `post_row`, `card`), nhớ `e()`.
3. Nếu cần tìm kiếm theo trường đó, thêm vào `build_search_data` và hàm `search` trong `main.js`.
4. Cập nhật bảng trường trong [03. Dữ liệu nguồn](03-du-lieu-nguon.md).

### Thêm một loại trang

Theo mẫu `build_login`:

```python
def build_trang_moi():
    root = ""                                   # theo độ sâu của trang
    page = head(root, "Tiêu đề", "Mô tả 120–160 ký tự.", "trang-moi.html", "assets/images/og-default.jpg")
    page += header(root)
    page += f"""<main id="main">
  <div class="container">
    <h1>Tiêu đề</h1>
  </div>
</main>
"""
    page += footer(root)
    write("trang-moi.html", page)
```

Gọi hàm trong `main()`, thêm URL vào `build_sitemap` nếu cần index, build rồi chạy `check_site.py` (mỗi trang
phải có đúng một `<h1>`, có title, description, canonical).

### Thêm mục menu hoặc chuyên mục

Thêm mục vào `sections` của `nav.json` với `slug` và `groups`. Mục mới tự có trang hub, các trang chủ đề, được
nhận làm `category` cho bài, xuất hiện ở cột "Khám phá" chân trang và sidebar "Chuyên mục". Trang chủ chỉ hiện
những mục được liệt kê cứng trong `build_home`; thêm vào `explore_data` nếu muốn có thẻ ở đó. `make_thumbs.py`
cũng tự đọc tên mục mới cho nhãn ảnh đại diện.

### Phong cách code

- Tiếng Việt có dấu trong chú thích, docstring, thông báo `assert`.
- Hàm dựng HTML trả về chuỗi; không ghi file ngoài `write()`.
- Giữ build tất định: cùng dữ liệu, cùng ngày thì ra cùng file (dễ đọc diff).
- Không thêm phụ thuộc ngoài thư viện chuẩn cho `build.py` và `check_site.py`.
