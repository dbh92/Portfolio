# 08. Kiểm tra và xử lý lỗi

## `tools/check_site.py`

Dự án không có bộ test; `check_site.py` là bước kiểm tra bắt buộc sau mỗi lần build. Nó đọc site **đã build**
trên đĩa (không tự build), chỉ dùng thư viện chuẩn.

```bash
python tools/build.py && python tools/check_site.py
```

Kết quả tốt:

```
513 trang, 388 bài, 1192 khối code Python
OK: không có lỗi
```

Có lỗi: in `N LỖI:` và tối đa 80 dòng lỗi, thoát với mã 1 (dùng được trong script và CI).

### Những gì được kiểm tra

**Mọi trang HTML đã build** (mọi `**/*.html` trừ `src/`, `tools/`, `node_modules/`):

| Kiểm tra | Lỗi in ra |
|---|---|
| Mọi `href`/`src` nội bộ trỏ tới file có thật. Bỏ qua `http…`, `mailto:`, `tel:`, `data:`, `javascript:`, link chỉ có `#…`. Đường dẫn kết thúc `/` hoặc là thư mục thì tìm `index.html`; `?v=…` được bỏ. | `link hỏng: <trang> → <url>` |
| Phần `#anchor` của link tới trang `.html` khác tồn tại dưới dạng `id="…"` trong trang đích | `anchor hỏng: <trang> → <url>` |
| Đúng một `<h1>` | `số h1 khác 1: <trang>` |
| Có `<title>`, `<meta name="description"`, `<link rel="canonical"` | `thiếu <thẻ> trong <trang>` |
| Mọi khối `<script type="application/ld+json">` là JSON hợp lệ | `JSON-LD lỗi: <trang> <chi tiết>` |

Trang chuyển hướng (`http-equiv="refresh"`) chỉ được kiểm tra link, không kiểm tra SEO.

Lưu ý: link `#anchor` **trong cùng trang** (`href="#muc"`) không được kiểm tra vì bị bỏ qua ở bước đầu.

**Mọi thân bài `src/posts/*.html`:**

| Kiểm tra | Lỗi in ra |
|---|---|
| Thẻ mở/đóng cân bằng (bỏ qua thẻ rỗng `br`, `img`, `hr`, `input`…) | `thẻ HTML không cân bằng: <file> [thẻ đóng sai] [thẻ chưa đóng]` |
| Không có `<h1>` | `thân bài không được có <h1>: <file>` |
| Trong `<pre><code>`: không có `<` chưa escape (trừ thẻ `span`, `b`, `i`, `em`, `strong`) | `ký tự < chưa escape trong <pre><code>: <file> <đoạn đầu>` |
| Trong `<pre><code>`: mọi `&` là thực thể hợp lệ (`&lt;`, `&gt;`, `&amp;`, `&quot;`, `&apos;`, `&nbsp;`, `&#…;`) | `ký tự & chưa escape trong <pre><code>: <file>` |
| Khối trông giống Python được `ast.parse` | `code Python lỗi cú pháp: <file> dòng N: <thông báo>` |

Cách nhận diện khối Python và cách bỏ qua khối cố ý sai: xem [04. Viết bài](04-viet-bai.md#code-mẫu).

**Dữ liệu `src/posts.json`:**

| Kiểm tra | Lỗi in ra |
|---|---|
| Không có slug trùng | `slug bài viết bị trùng` |
| Mỗi bài có `src/posts/<slug>.html`, `assets/images/posts/<slug>.jpg`, `.webp` | `thiếu file: <đường dẫn>` |

### Những gì không được kiểm tra

Cần tự xem bằng mắt hoặc kiểm tra tay:

- Nội dung có đúng sự thật, code có **chạy** đúng không (chỉ kiểm tra cú pháp).
- Link ra ngoài còn sống không.
- Độ dài `title`/`excerpt`, số từ của bài.
- Id tiêu đề trùng nhau trong một bài, anchor trong cùng trang.
- Công thức KaTeX có lỗi không (chỉ thấy khi mở trang).
- Giao diện trên điện thoại, chế độ tối.
- Code C#, bash, YAML… (chỉ Python được parse).

## Lỗi thường gặp và cách sửa

### Lỗi khi chạy công cụ

**`UnicodeEncodeError: 'charmap' codec can't encode character …`** (Windows)

Console Windows dùng bảng mã cp1252 nên không in được chữ tiếng Việt mà các script in ra. Lỗi xảy ra **khi in**,
không phải khi đọc dữ liệu: `check_site.py` có thể dừng trước khi báo kết quả; `build.py` có thể đã ghi xong mọi
trang rồi mới lỗi ở dòng "Xong: …". Chạy ở chế độ UTF-8:

```bash
python -X utf8 tools/build.py
python -X utf8 tools/check_site.py
```

hoặc đặt biến môi trường một lần cho cả phiên: `set PYTHONIOENCODING=utf-8` (cmd),
`$env:PYTHONIOENCODING = "utf-8"` (PowerShell), `export PYTHONIOENCODING=utf-8` (Git Bash). Terminal của VS Code
thường đã là UTF-8.

**`ModuleNotFoundError: No module named 'PIL'`** khi chạy `make_thumbs.py`: `pip install Pillow`.

**`AssertionError: …`** khi build: đọc thông báo tiếng Việt, đối chiếu bảng ở
[06. Bên trong build.py](06-build-py.md#các-kiểm-tra-khi-nạp-dữ-liệu).

**`json.decoder.JSONDecodeError: … line L column C`**: JSON sai cú pháp ở dòng L. Hay gặp nhất: dấu phẩy thừa sau
phần tử cuối, thiếu dấu phẩy giữa hai bài, dấu nháy kép trong chuỗi chưa escape (`\"`). Tìm nhanh:
`python -m json.tool src/posts.json > /dev/null`.

### Lỗi do `check_site.py` báo

| Lỗi | Cách sửa |
|---|---|
| `link hỏng: hoc/a.html → b.html` | Bài `b` không cùng chuyên mục với `a`: đổi thành `../<chuyên-mục>/b.html`. Hoặc slug gõ sai, hoặc bài đích đã bị xóa. Lỗi nằm trong `src/posts/a.html`, không phải trong file sinh ra. |
| `link hỏng: …/old.html` sau khi xóa bài | Còn bài khác link tới bài đã xóa: `grep -rn "old.html" src/` |
| `anchor hỏng: … → x.html#muc` | Id được sinh từ chữ tiêu đề; xem `id` thật bằng `grep -o 'id="[^"]*"' <chuyên-mục>/x.html` rồi sửa link |
| `số h1 khác 1` | Thường do thân bài có `<h1>`. Đổi thành `<h2>`. |
| `thẻ HTML không cân bằng: … ['p'] ['div']` | Danh sách đầu là thẻ đóng không khớp, danh sách sau là thẻ chưa đóng. Hay gặp: quên `</div>` của `.ex`, `</details>`, đóng `</li>` sai thứ tự, `<p>` chứa `<ul>` (đóng ngầm) |
| `ký tự < chưa escape trong <pre><code>` | Thay `<` bằng `&lt;`, `>` bằng `&gt;` trong code (so sánh, generic C#, HTML mẫu) |
| `ký tự & chưa escape trong <pre><code>` | Thay `&` bằng `&amp;` (`&&` → `&amp;&amp;`) |
| `code Python lỗi cú pháp: … dòng N` | Số dòng tính trong khối code. Kiểm tra thụt lề, dấu ngoặc, cú pháp mới hơn Python 3.10. Khối cố ý sai: thêm `(minh họa)` vào chú thích. Khối không phải Python mà bị nhận nhầm: đổi dòng đầu (ví dụ thêm `$ ` trước lệnh shell). |
| `thiếu file: assets/images/posts/<slug>.jpg` | Chạy `python tools/make_thumbs.py` |
| `thiếu file: src/posts/<slug>.html` | Tạo thân bài, hoặc xóa dòng bài thừa trong `posts.json` |
| `slug bài viết bị trùng` | Tìm `grep -o '"slug": "[^"]*"' src/posts.json \| sort \| uniq -d` |

### Lỗi hiển thị sau khi đăng

| Hiện tượng | Nguyên nhân, cách sửa |
|---|---|
| Bài mới không hiện trên trang chủ đề | `tags` của bài không có tag nào của chủ đề trong `nav.json` |
| Bài không hiện ở "Bài viết mới" trang chủ | Trang chủ lấy tối đa 2 bài mỗi chuyên mục trong 5 bài; bài cùng ngày với nhiều bài khác cùng chuyên mục có thể bị đẩy ra |
| Bài mới không tìm thấy bằng `Ctrl K` | Chưa commit `assets/js/search-data.js`, hoặc trình duyệt giữ bản cũ (build lại ngày mới đổi `?v=`; tải lại cứng `Ctrl F5`) |
| CSS/JS sửa rồi mà trang không đổi | Trình duyệt cache: build lại để đổi `?v=` (chỉ đổi khi build ngày khác), hoặc `Ctrl F5` |
| Bảng có hai lớp viền | Thân bài tự bọc `<div class="table-wrap">`, `main.js` bọc thêm lớp nữa. Bỏ lớp bọc trong thân bài. |
| Công thức hiện nguyên `\( … \)` | Bài thiếu `"math": true` trong `posts.json` |
| Công thức hiện màu đỏ | Lỗi cú pháp LaTeX; thử công thức trên katex.org |
| Hộp tải có dòng "đang được hoàn thiện" | `downloads.<key>.ready` chưa là `true` |
| Trang cũ vẫn mở được sau khi xóa bài/chủ đề | Build không xóa file; `git rm` trang cũ |
| Ảnh đại diện vẫn là ảnh cũ sau khi đổi `thumb` | `make_thumbs.py` chỉ vẽ ảnh chưa có. Xóa `<slug>.jpg` và `<slug>.webp` rồi chạy lại (đừng dùng `--all` nếu có ảnh thật) |
| Chữ Hán trên ảnh đại diện thành ô vuông | Máy thiếu font CJK (`msyhbd.ttc` trên Windows, `wqy-zenhei.ttc` trên Linux) |
| Tên miền hocfree.vn không vào được site | Kiểm tra file `CNAME` và Settings → Pages (xem [02](02-cai-dat-build-trien-khai.md#tên-miền-hocfreevn)) |
| Tiến độ học bị mất | Lưu trong `localStorage` theo trình duyệt và theo slug: đổi trình duyệt, xóa dữ liệu, hoặc đổi slug lộ trình/chặng/bài |

## Trước khi đẩy lên `main`

```bash
python -X utf8 tools/build.py
python -X utf8 tools/check_site.py     # OK: không có lỗi
git status                             # có cả nguồn và file sinh ra?
git diff --stat
```

Diff chỉ có dòng `?v=` thay đổi ở hàng trăm trang là do build vào ngày mới, bình thường.
