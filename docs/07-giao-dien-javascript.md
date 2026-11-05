# 07. Giao diện và JavaScript

Phía trình duyệt gồm hai file CSS (`assets/css/fonts.css`, `assets/css/style.css`) và hai file JavaScript
(`assets/js/search-data.js` sinh ra, `assets/js/main.js` viết tay). Không framework, không bước biên dịch:
sửa file, build lại (để cập nhật `?v=`), tải lại trang.

## CSS

### Tổ chức `style.css`

File khoảng 1.100 dòng, chia khối bằng chú thích `/* ---------- … ---------- */` theo thứ tự:

1. Biến thiết kế (`:root`, `html.dark`) và nền tảng (reset, chữ, `:focus-visible`, thanh tiến độ đọc).
2. Header, menu chính, mega menu, dropdown, thẻ Learning Path, dải 3 bước, hộp tìm kiếm.
3. Nút, nhãn, tiêu đề khu vực.
4. Trang chủ: hero, mô phỏng Vision, dải công nghệ, 3 bước, lộ trình nổi bật, chủ đề, bài mới, khám phá, CTA.
5. Trang trong: đầu trang, danh sách bài, sidebar, bài viết (`.prose`), hộp tải, hub, chủ đề, roadmap lộ trình,
   404, footer.
6. Responsive.
7. Giáo trình: thanh khóa học, mục lục chặng, trang chặng, banner trang chủ đề.
8. Khối nội dung đặc biệt trong bài: bài tập, `tip`/`warn`, hội thoại, sơ đồ SVG, ma trận, KaTeX.

Thêm CSS mới vào đúng khối chức năng, viết chú thích tiếng Việt cho quy tắc không hiển nhiên.

### Biến thiết kế

Dùng biến thay cho màu cố định để chế độ tối tự đúng:

| Nhóm | Biến |
|---|---|
| Nền, bề mặt | `--bg`, `--bg-soft`, `--surface`, `--surface-2` |
| Chữ | `--text`, `--text-2`, `--muted` |
| Đường kẻ | `--line`, `--line-soft` |
| Màu nhấn (cam HọcFree `#f04e23`) | `--accent`, `--accent-2`, `--accent-ink` (chữ màu nhấn đủ tương phản), `--accent-soft`, `--accent-line`, `--grad` |
| Khối tối (hero, thẻ lộ trình, footer) | `--ink`, `--ink-2`, `--ink-text`, `--ink-line` |
| Code | `--code-bg`, `--code-text` |
| Bóng, bo góc | `--shadow-xs`, `--shadow`, `--shadow-lg`, `--radius-sm` (10px), `--radius` (14px), `--radius-lg` (22px) |
| Header | `--top-h` (64px), `--nav-h` (48px), `--header-h` |
| Font | `--font` (Be Vietnam Pro), `--mono` (JetBrains Mono) |

`html.dark` ghi đè các biến trên. Quy tắc riêng cho chế độ tối viết dạng `html.dark .lop { … }`.

### Bố cục và điểm ngắt

- `.container`: rộng tối đa 1240px, lề 24px; `.container.wide`: 1400px (header, mega menu).
- `.layout`: lưới nội dung + sidebar 320px.

| Điểm ngắt | Thay đổi chính |
|---|---|
| `≤ 1340px` | Mega menu thu hẹp |
| `≤ 1080px` | Sidebar xuống dưới nội dung (2 cột), footer 2 cột, bản đồ lộ trình thu gọn, hero 1 cột |
| `≤ 1060px` | Menu thành drawer (nút hamburger), panel thành accordion. `main.js` dùng mốc `min-width: 1061px` cho chế độ desktop, phải khớp với CSS. |
| `≤ 900px`, `≤ 640px` | Lưới 1 cột, chữ và khoảng cách nhỏ lại |
| `prefers-reduced-motion` | Tắt transition, animation, cuộn mượt |

### Font

`fonts.css` khai `@font-face` cho Be Vietnam Pro (400, 500, 600, 700, 800) và JetBrains Mono (400), mỗi độ đậm
3 subset `vietnamese`, `latin`, `latin-ext` với `unicode-range` và `font-display: swap`. Nguồn: Fontsource,
giấy phép SIL OFL 1.1 (`assets/fonts/OFL.txt`). `build.py` preload 3 file hay dùng nhất (`PRELOAD_FONTS`).
`tools/fonts/` chứa bản TTF riêng cho `make_thumbs.py`.

### Icon

Icon Lucide được chèn nội tuyến dạng `<svg viewBox="0 0 24 24">`. CSS đặt cho **mọi** `<svg>` mặc định
20×20px, `fill: none`, `stroke: currentColor`, nét 2px bo tròn, nên icon tự lấy màu chữ. SVG không phải icon
(sơ đồ `.dg` trong bài, hình hero `.mock-view`) phải ghi đè các giá trị này. Xem cách thêm icon ở
[03](03-du-lieu-nguon.md#srciconsjson).

## JavaScript: `assets/js/main.js`

Một IIFE `"use strict"`, cú pháp ES5 (`var`, `function`), không phụ thuộc. Mỗi khối tự kiểm tra phần tử có
trên trang không trước khi chạy, nên cùng một file dùng được cho mọi loại trang.

### Dark mode

- Một đoạn script nội tuyến trong `<head>` (do `head()` trong `build.py` sinh) đọc `localStorage["hf-theme"]`;
  nếu không có thì theo `prefers-color-scheme`. Thêm lớp `dark` vào `<html>` **trước khi vẽ** để không nháy trắng.
- Nút `.theme-toggle` đảo lớp `dark` và lưu `"dark"` hoặc `"light"`. Đã bấm một lần thì trang không còn theo
  cài đặt hệ thống nữa (muốn theo lại: xóa khóa `hf-theme`).

### Menu

- Mỗi mục có panel là một nút `.nav-trigger` (`aria-expanded`, `aria-controls`), không phải link.
- Desktop (`≥ 1061px`, có chuột): mở khi rê chuột (trễ 90ms, đóng sau 180ms để không nháy khi lướt ngang), mở/đóng
  khi bấm, `↓` mở panel và đưa focus vào link đầu, `Esc` đóng và trả focus về nút, bấm ra ngoài thì đóng.
- Mobile: nút hamburger mở drawer `.site-nav.open`, tự mở mục đang active; `Esc`, nút đóng hoặc lớp phủ thì
  đóng. Đổi kích thước qua mốc desktop thì drawer tự đóng.

### Tìm kiếm

- Mở hộp: bấm nút tìm kiếm, `Ctrl K` / `⌘K`, hoặc `/` khi không đang gõ. `Esc` hoặc lớp phủ thì đóng; focus bị
  giữ trong hộp (Tab vòng), đóng thì trả focus về chỗ cũ. Trên Mac, nhãn phím đổi thành `⌘K`.
- Chuẩn hóa từ khóa và dữ liệu: chữ thường, bỏ dấu, `đ` → `d`. Gõ "hieu chuan" vẫn ra "hiệu chuẩn".
- **Bài viết** (`search`): mọi từ phải có trong tiêu đề + excerpt + tag + tên chuyên mục; từ có trong tiêu đề
  được 3 điểm, ở chỗ khác 1 điểm; sắp theo điểm.
- **Chủ đề, lộ trình, chặng** (`searchTopics`): mọi từ phải có trong tên + tên mục + tên nhóm; ưu tiên lộ trình
  flagship, rồi tên bắt đầu bằng từ khóa, rồi lộ trình/chặng, rồi chủ đề nhiều bài.
- Hộp gợi ý: tối đa 5 chủ đề/lộ trình và 6 bài; `↑`/`↓` chọn, `Enter` mở mục đang chọn, `Enter` khi không chọn
  thì sang `search.html?q=…`. Từ khóa được tô bằng `<mark>`; mọi chuỗi đều qua `escapeHtml`.
- `search.html`: đọc `?q=`, hiện số kết quả, chip chủ đề liên quan (tối đa 8) và danh sách bài. Không có `q` thì
  liệt kê mọi bài.

### Tiến độ lộ trình và bài học

Khối này đọc và ghi `localStorage`, giao tiếp với HTML qua thuộc tính `data-*` do `build.py` sinh. Đây là
**hợp đồng giữa `build.py` và `main.js`**: đổi tên một thuộc tính ở bên này phải đổi ở bên kia.

| Thuộc tính | Đặt ở | Ý nghĩa |
|---|---|---|
| `data-root` | `<html>` | Tiền tố đường dẫn tương đối (`""`, `"../"`, `"../../"`, `"/"`) |
| `data-path` | `<main>` trang lộ trình | Slug lộ trình; bật khối tiến độ chặng, khóa `hf-path-<slug>` |
| `data-step` | `.step` | Slug chặng |
| `data-step-check` | checkbox | "Đã hoàn thành chặng" |
| `data-map-step` | link trong bản đồ | Tô trạng thái đã xong / đang học |
| `data-progress-text`, `data-progress-bar` | | Chữ "N/M chặng" và thanh tiến độ |
| `data-path-continue` | nút đầu trang | Đổi thành "Tiếp tục: Chặng N · …" hoặc "Bạn đã hoàn thành lộ trình 🎯" |
| `data-course` | trang lộ trình, trang chặng, các khối của trang bài học | Slug lộ trình; bật khối tiến độ bài học, khóa `hf-lessons-<slug>` |
| `data-lesson` | dòng bài học (`li`) | Thêm lớp `is-done` khi đã học |
| `data-lesson-check` | checkbox trên trang chặng | Đánh dấu đã học |
| `data-lesson-done` | nút trên trang bài học | Bật/tắt đã học (`aria-pressed`) |
| `data-lesson-count` | khối đếm | Danh sách slug cách nhau bởi dấu cách; đếm số đã học |
| `data-lc-text`, `data-lc-bar` | bên trong khối đếm | Chữ "N/M bài" và thanh tiến độ |
| `data-lesson-link` | link bài trên trang chặng | Tìm bài chưa học đầu tiên |
| `data-lesson-continue` | nút "Bắt đầu bài 1" | Đổi thành "Học tiếp: …" hoặc "Đã học hết chặng này ✓ Ôn lại" |

Khóa `localStorage`:

| Khóa | Giá trị |
|---|---|
| `hf-theme` | `"dark"` hoặc `"light"` |
| `hf-path-<path>` | JSON mảng slug chặng đã hoàn thành |
| `hf-lessons-<path>` | JSON mảng slug bài đã học |

Mọi truy cập `localStorage` nằm trong `try/catch`: trình duyệt chặn lưu trữ (chế độ riêng tư) thì trang vẫn chạy,
chỉ không nhớ tiến độ.

### Bài viết

- Bọc mỗi `.prose table` trong `<div class="table-wrap">` để cuộn ngang trên màn hình hẹp.
- Thêm nút "Sao chép" vào mỗi `.prose pre` (sao chép `innerText` của `<code>`). Dùng `navigator.clipboard` khi ở
  ngữ cảnh an toàn (HTTPS, localhost), nếu không thì dùng `textarea` + `execCommand("copy")`.
- Nút sao chép liên kết `.copy-link` ở phần chia sẻ.
- Thanh tiến độ đọc `.progress` theo vị trí cuộn trong `.prose`; nút `.to-top` hiện sau 600px; header có bóng
  khi cuộn (`.scrolled`).

## KaTeX

Bài có `"math": true` tải `assets/vendor/katex/katex.min.css`, `katex.min.js` và `contrib/auto-render.min.js`
(KaTeX 0.16.11, giấy phép MIT trong `assets/vendor/katex/LICENSE`). `auto-render` chạy trên `.prose` với dấu
`\[ … \]` (dòng riêng) và `\( … \)` (cùng dòng), `throwOnError: false`. Nâng cấp KaTeX: thay cả thư mục
`assets/vendor/katex/` bằng bản mới (gồm `fonts/`) và cập nhật số phiên bản trong docstring của `math_head()`.

## Khả năng tiếp cận

Những điều đang có, cần giữ khi sửa giao diện:

- Link "Bỏ qua đến nội dung" (`.skip-link` → `#main`) ở đầu mọi trang.
- Một `<h1>` mỗi trang (được `check_site.py` kiểm tra); tiêu đề theo cấp.
- Menu dùng nút có `aria-expanded`/`aria-controls`; mục hiện tại có `aria-current`.
- Hộp tìm kiếm `role="dialog" aria-modal="true"`, giữ focus, `aria-live` cho gợi ý.
- Icon trang trí có `aria-hidden="true"`; nút chỉ có icon có `aria-label`.
- Ảnh bìa bài viết có `alt` là tiêu đề; ảnh nhỏ trong danh sách có `alt=""` vì tiêu đề đã nằm cạnh.
- Viền focus rõ (`:focus-visible`, màu nhấn), tôn trọng `prefers-reduced-motion`.
- Mọi ảnh có `width`/`height` để không nhảy bố cục; ảnh ngoài màn hình đầu dùng `loading="lazy"`.

## PWA và icon

`site.webmanifest` khai tên, màu chủ đạo `#f04e23`, icon 192 và 512 (`assets/images/icon-*.png`). Có
`favicon.svg` và `apple-touch-icon.png`. Không có service worker: site không chạy ngoại tuyến.
