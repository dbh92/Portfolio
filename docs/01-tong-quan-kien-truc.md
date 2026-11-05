# 01. Tổng quan và kiến trúc

## HọcFree là gì

HọcFree (hocfree.vn) là website học miễn phí cho người Việt về AI, Computer Vision, Machine Vision,
lập trình và ngoại ngữ (TOEIC, HSK). Không quảng cáo, không tài khoản: mọi bài đọc được ngay, tiến độ
học lưu trong trình duyệt của người học.

Nội dung được tổ chức theo hành trình ba bước, hiện trên menu và trang chủ:

| Bước | Mục menu | Thư mục | Vai trò |
|---|---|---|---|
| 1 · Học | Học AI & Lập trình | `hoc/` | Bài học theo chủ đề (mega menu 4 nhóm) |
| 2 · Thực hành | Projects | `projects/` | Dự án có mã nguồn |
| 3 · Trở thành kỹ sư | Learning Paths | `lo-trinh/` | Lộ trình nghề nghiệp có thứ tự |
| Khám phá | Kiến thức, Tin tức AI, Ngoại ngữ, Tài nguyên | `kien-thuc/` `tin-tuc-ai/` `ngoai-ngu/` `tai-nguyen/` | Bài chuyên đề, tin tức, ngoại ngữ, tài liệu |

Số liệu ngày 05/11/2026:

| Chuyên mục | Số bài |
|---|---|
| `hoc` | 162 |
| `ngoai-ngu` | 127 |
| `kien-thuc` | 34 |
| `projects` | 26 |
| `tai-nguyen` | 23 |
| `tin-tuc-ai` | 16 |
| **Tổng** | **388** |

| Lộ trình | Chặng | Giai đoạn | Bài học khai báo | Thời lượng |
|---|---|---|---|---|
| `vision-engineer` (flagship) | 15 | 5 | 123 | ~13 tháng, 8–10 giờ/tuần |
| `python-developer` | 10 | 4 | 53 | ~6 tháng, 8–10 giờ/tuần |
| `toeic-700` | 11 | 5 | 60 | ~5 tháng, 60–90 phút/ngày |
| `hsk3` | 10 | 5 | 61 | ~6 tháng, 60 phút/ngày |

## Nguyên tắc kỹ thuật

- **Tĩnh hoàn toàn.** HTML, CSS, JavaScript thuần. Không framework, không bundler, không npm, không
  backend. GitHub Pages phục vụ thẳng các file trong nhánh `main`.
- **Một trình sinh trang duy nhất.** `tools/build.py` (Python thuần, chỉ dùng thư viện chuẩn) đọc dữ liệu
  trong `src/` và ghi ra mọi trang HTML. Không có template engine: HTML được ghép bằng f-string.
- **Dữ liệu tách khỏi trình bày.** Danh sách bài, menu, lộ trình nằm trong JSON; nội dung bài nằm trong
  các đoạn HTML `src/posts/<slug>.html`; khung trang nằm trong `build.py`.
- **Tự host mọi tài nguyên.** Font (Be Vietnam Pro, JetBrains Mono), icon (Lucide), KaTeX đều nằm trong
  repo. Trang không gọi CDN hay dịch vụ bên thứ ba nào khi tải.
- **Kiểm tra thay cho test.** `tools/check_site.py` là bộ kiểm thử duy nhất: link, anchor, SEO tối thiểu,
  HTML thân bài, cú pháp code Python mẫu.

## Luồng dữ liệu

```
src/posts.json ─────────┐
src/posts/<slug>.html ──┤
src/nav.json ───────────┼──► tools/build.py ──► *.html (trang chủ, chuyên mục, chủ đề, bài, lộ trình…)
src/learning-paths.json ┤                   ├─► assets/js/search-data.js (chỉ mục tìm kiếm)
src/icons.json ─────────┘                   └─► sitemap.xml, robots.txt

src/posts.json + src/nav.json ──► tools/make_thumbs.py ──► assets/images/posts/<slug>.jpg + .webp

*.html ──► tools/check_site.py ──► "OK: không có lỗi" hoặc danh sách lỗi (exit 1)

Trình duyệt: *.html + assets/css/*.css + assets/js/search-data.js + assets/js/main.js
```

`build.py` kiểm tra dữ liệu đầu vào bằng `assert` ngay khi nạp, trước khi ghi bất cứ file nào. Dữ liệu
sai (chuyên mục không tồn tại, bài đọc thêm trỏ tới slug không có…) làm build dừng và không đụng tới site
hiện tại.

## Cấu trúc thư mục

```
.
├── index.html, search.html, gioi-thieu.html, dang-nhap.html, 404.html   ← sinh ra
├── hoc/ projects/ kien-thuc/ tin-tuc-ai/ ngoai-ngu/ tai-nguyen/          ← sinh ra
│   ├── index.html            trang tổng của mục (hub)
│   ├── <chủ-đề>.html         trang chủ đề: liệt kê bài có tag khớp
│   └── <slug-bài>.html       trang bài viết thuộc chuyên mục này
├── lo-trinh/                                                             ← sinh ra
│   ├── index.html            danh sách lộ trình
│   ├── <lộ-trình>.html       bản đồ lộ trình: giai đoạn → chặng
│   └── <lộ-trình>/
│       ├── index.html        trang chuyển hướng về <lộ-trình>.html
│       └── <chặng>.html      trang chặng: bài học theo thứ tự
├── sitemap.xml, robots.txt                                               ← sinh ra
├── site.webmanifest, .nojekyll                                           ← viết tay
├── src/                                                                  ← NGUỒN
│   ├── posts.json            thông tin site, link tải, bài "đọc nhiều", danh sách bài
│   ├── posts/<slug>.html     thân bài (đoạn HTML)
│   ├── nav.json              menu: mục → nhóm → chủ đề
│   ├── learning-paths.json   lộ trình → giai đoạn, chặng → bài học
│   ├── icons.json            icon Lucide (phần trong thẻ <svg>)
│   └── editorial-plan.json   kế hoạch đăng bài tự động
├── tools/
│   ├── build.py              sinh site
│   ├── check_site.py         kiểm tra site
│   ├── make_thumbs.py        vẽ ảnh đại diện (cần Pillow)
│   └── fonts/                font TTF dùng khi vẽ ảnh đại diện
├── assets/
│   ├── css/style.css         toàn bộ giao diện (sáng/tối, responsive)
│   ├── css/fonts.css         @font-face cho font tự host
│   ├── js/main.js            hành vi phía trình duyệt
│   ├── js/search-data.js     chỉ mục tìm kiếm (sinh ra)
│   ├── fonts/                woff2: Be Vietnam Pro, JetBrains Mono (SIL OFL 1.1)
│   ├── images/               favicon, icon PWA, og-default.jpg
│   ├── images/posts/         ảnh đại diện bài: <slug>.webp và <slug>.jpg
│   └── vendor/katex/         KaTeX 0.16.11 tự host
└── docs/                     tài liệu này và quy trình đăng bài tự động
```

## Các loại trang và URL

| Loại trang | URL | Hàm trong `build.py` | Số trang (05/11/2026) |
|---|---|---|---|
| Trang chủ | `/` (`index.html`) | `build_home` | 1 |
| Trang tổng mục (hub) | `/<mục>/` | `build_hub` | 6 |
| Trang chủ đề | `/<mục>/<chủ-đề>.html` | `build_topic` | 59 |
| Bài viết | `/<chuyên-mục>/<slug>.html` | `build_post` | 388 |
| Danh sách lộ trình | `/lo-trinh/` | `build_paths_index` | 1 |
| Bản đồ lộ trình | `/lo-trinh/<lộ-trình>.html` | `build_path` | 4 |
| Trang chặng | `/lo-trinh/<lộ-trình>/<chặng>.html` | `build_step` | 46 |
| Chuyển hướng thư mục lộ trình | `/lo-trinh/<lộ-trình>/` | `main` | 4 |
| Tìm kiếm, Giới thiệu, Đăng nhập, 404 | `search.html` … | `build_search`, `build_about`, `build_login`, `build_404` | 4 |

Một bài viết có thể đồng thời là **bài học** của một chặng lộ trình. Trang bài học vẫn nằm ở
`/<chuyên-mục>/<slug>.html` nhưng có thêm thanh khóa học, mục tiêu, bài tập, nút "Đánh dấu đã học xong"
và điều hướng theo thứ tự giáo trình. Xem [05. Learning Paths](05-lo-trinh-hoc.md).

## Ba khái niệm dễ nhầm

- **Chuyên mục** (`category` của bài): quyết định *bài nằm ở thư mục nào*. Mỗi bài có đúng một chuyên mục,
  là một trong 6 mục có `groups` trong `nav.json`.
- **Chủ đề** (item trong `nav.json`): một trang tập hợp. Bài hiện trên trang chủ đề khi **tag** của bài khớp
  tag của chủ đề. Một bài có thể xuất hiện ở nhiều chủ đề, kể cả chủ đề thuộc mục khác chuyên mục của bài.
- **Bài học** (lesson trong `learning-paths.json`): một bài viết được xếp vào giáo trình. Thứ tự học do
  `learning-paths.json` quyết định, không phụ thuộc ngày đăng.

Ví dụ: bài `python-2-bien-kieu-du-lieu-toan-tu` có chuyên mục `hoc` (nằm ở `hoc/…html`), có tag `Python`
(hiện trên `hoc/python.html`), và là bài 2 của chặng 1 lộ trình Vision Engineer.

## Phía trình duyệt

Mỗi trang tải đúng hai file JavaScript, đều `defer`:

- `assets/js/search-data.js`: gán `window.HF_POSTS` (mọi bài) và `window.HF_TOPICS` (chủ đề, lộ trình,
  chặng) để tìm kiếm tức thì mà không cần máy chủ.
- `assets/js/main.js`: dark mode, menu, hộp tìm kiếm `Ctrl K`, nút sao chép code, tiến độ đọc, tiến độ
  lộ trình và bài học lưu trong `localStorage`.

Trang có `"math": true` tải thêm KaTeX. Chi tiết ở [07. Giao diện và JavaScript](07-giao-dien-javascript.md).

## Lịch sử ngắn

- 02/10/2026: khởi tạo website, 3 chuyên mục, 15 bài mẫu.
- 10/10/2026: chạy quy trình đăng 10 bài/ngày tự động theo `src/editorial-plan.json` (ngày 1/20 đã đăng).
- 29/10/2026: thêm lộ trình Python Developer (10 chặng, 53 bài `pydev-*`).
- Xem đầy đủ bằng `git log --oneline`.
