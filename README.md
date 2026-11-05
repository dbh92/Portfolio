# HọcFree.vn

Website tĩnh (HTML + CSS + JavaScript thuần) chia sẻ kiến thức lập trình, ngoại ngữ và blog, chạy trên **GitHub Pages** với tên miền **hocfree.vn**.

> Tài liệu đầy đủ (kiến trúc, dữ liệu, viết bài, lộ trình, build, giao diện, xử lý lỗi): xem [`docs/`](docs/README.md).

## Cấu trúc

```
index.html                 Trang chủ
hoc/ projects/ lo-trinh/   Các mục menu: trang tổng, trang chủ đề và bài viết của mục
kien-thuc/ tin-tuc-ai/ ngoai-ngu/ tai-nguyen/
search.html, gioi-thieu.html, dang-nhap.html, 404.html
assets/css/style.css       Giao diện (sáng/tối, responsive)
assets/css/fonts.css       Khai báo font tự host (assets/fonts/)
assets/js/main.js          Tìm kiếm, menu mobile, copy code, dark mode…
assets/js/search-data.js   Chỉ mục tìm kiếm (tự sinh)
assets/images/posts/       Ảnh đại diện bài viết 1200x675: .webp hiển thị trên trang, .jpg cho og:image
site.webmanifest           Thông tin ứng dụng web (tên, icon)
src/posts.json             Thông tin website, danh sách bài viết, bài "đọc nhiều"
src/posts/<slug>.html      Nội dung từng bài (chỉ phần thân)
src/nav.json               Menu chính: mục → nhóm → chủ đề
src/learning-paths.json    Learning Paths (lộ trình Vision Engineer…)
src/icons.json             Icon Lucide dùng trong trang (SVG nội tuyến)
tools/build.py             Sinh toàn bộ trang HTML từ src/
tools/make_thumbs.py       Vẽ ảnh đại diện tự động (JPG + WebP)
tools/check_site.py        Kiểm tra site sau khi build (link, SEO, HTML thân bài, code Python)
tools/fonts/               Font Be Vietnam Pro (TTF) để vẽ ảnh đại diện
CNAME                      Tên miền riêng: hocfree.vn (hiện chưa có trong repo, xem docs/02)
docs/                      Tài liệu dự án
```

> Các file `.html` ở thư mục gốc và trong các mục được **sinh tự động**, hãy sửa trong `src/` rồi build lại.

## Thêm bài viết mới

1. Thêm một mục vào `posts` trong `src/posts.json`, ví dụ:
   ```json
   {
     "slug": "opencv-doc-anh-tu-camera",
     "category": "hoc",
     "title": "OpenCV: đọc ảnh từ camera",
     "excerpt": "…",
     "date": "2026-10-10",
     "tags": ["OpenCV", "Python"],
     "thumb": { "glyph": "CV", "colors": ["#ff6a3d", "#1b2a49"] }
   }
   ```
   - `category` là một mục menu: `hoc`, `projects`, `kien-thuc`, `tin-tuc-ai`, `ngoai-ngu`, `tai-nguyen`.
     Bài nằm ở `<category>/<slug>.html`.
   - `tags` quyết định bài hiện ở trang chủ đề nào (khớp với `tags` của chủ đề trong `src/nav.json`).
2. Tạo file `src/posts/<slug>.html` chứa phần thân bài (`<h2>`, `<p>`, `<ul>`, `<pre><code>`…).
3. Ảnh đại diện: chép ảnh thật vào `assets/images/posts/<slug>.jpg` (tỉ lệ 16:9), hoặc chạy
   `python tools/make_thumbs.py` để vẽ tự động.
4. `python tools/build.py`
5. `python tools/check_site.py` (phải in `OK: không có lỗi`)
6. `git add . && git commit -m "Thêm bài ..." && git push`

## Menu & kiến trúc thông tin

Menu được sinh từ `src/nav.json`, theo hành trình **Học → Thực hành → Trở thành kỹ sư**:

| Mục menu             | Vai trò                  | Trang                     |
|----------------------|--------------------------|---------------------------|
| Học AI & Lập trình   | Bước 1 · kiến thức, kỹ năng (mega menu) | `hoc/`     |
| Projects             | Bước 2 · thực hành       | `projects/`               |
| Learning Paths       | Bước 3 · định hướng nghề | `lo-trinh/`               |
| Kiến thức, Tin tức AI, Ngoại ngữ, Tài nguyên | khám phá | `kien-thuc/`, `tin-tuc-ai/`, `ngoai-ngu/`, `tai-nguyen/` |

- Menu chỉ chứa **chủ đề**, không chứa bài học. Mỗi chủ đề có trang riêng
  `<mục>/<chủ-đề>.html` tự liệt kê các bài có tag khớp với `tags` của chủ đề
  (có thể giới hạn thêm bằng `categories`). Viết thêm hàng nghìn bài thì menu vẫn giữ nguyên.
- Thêm chủ đề: thêm một `item` vào nhóm trong `src/nav.json` rồi build. Chủ đề chưa có bài
  hiển thị "Đang biên soạn" và được đặt `noindex`, không đưa vào sitemap.
- Ô tìm kiếm (`Ctrl K` hoặc `/`) tìm cả chủ đề, lộ trình và bài viết.
- Lộ trình **Vision Engineer** (`lo-trinh/vision-engineer.html`): 15 chặng, 5 giai đoạn; ngoài ra có
  Python Developer, 700+ TOEIC và HSK 3. Người học đánh dấu chặng và bài đã học, tiến độ lưu trên
  trình duyệt (localStorage). Xem [docs/05-lo-trinh-hoc.md](docs/05-lo-trinh-hoc.md).
- "Đăng nhập" hiện là trang giới thiệu (`dang-nhap.html`) vì website tĩnh chưa có tài khoản.

## Xem thử trên máy

```
python -m http.server 8000
```
Mở http://localhost:8000

## Trỏ tên miền → GitHub Pages

Tên miền mua tại Mắt Bão nhưng nameserver đang là **Cloudflare**
(`ned.ns.cloudflare.com`, `megan.ns.cloudflare.com`), nên bản ghi DNS phải thêm trong
Cloudflare → `hocfree.vn` → **DNS → Records** (thêm ở Mắt Bão sẽ không có tác dụng):

| Loại  | Name | Giá trị          | Proxy     |
|-------|------|------------------|-----------|
| A     | @    | 185.199.108.153  | DNS only  |
| A     | @    | 185.199.109.153  | DNS only  |
| A     | @    | 185.199.110.153  | DNS only  |
| A     | @    | 185.199.111.153  | DNS only  |
| CNAME | www  | dbh92.github.io  | DNS only  |

Sau khi DNS cập nhật: GitHub repo → Settings → Pages → Custom domain `hocfree.vn` → bật **Enforce HTTPS**.

## Font, icon, SEO

- **Font**: Be Vietnam Pro và JetBrains Mono tự host trong `assets/fonts/` (lấy từ Fontsource, giấy phép SIL OFL 1.1),
  chỉ gồm các subset vietnamese, latin, latin-ext. Không gọi Google Fonts nên tải nhanh hơn.
- **Icon**: [Lucide](https://lucide.dev) (ISC), lưu trong `src/icons.json`. Thêm icon: chép phần bên trong `<svg>`
  từ gói npm `lucide-static` vào file này, rồi dùng `icon("tên")` trong `tools/build.py`.
- **SEO**: mỗi trang có title, description riêng, canonical dạng thư mục (`/hoc/`), Open Graph + Twitter Card,
  JSON-LD (WebSite + SearchAction, Organization, Article, BreadcrumbList, CollectionPage, Course), `sitemap.xml`
  và `robots.txt`. Chủ đề chưa có bài để `noindex`.
