# 02. Cài đặt, build và triển khai

## Yêu cầu

| Công cụ | Dùng cho | Ghi chú |
|---|---|---|
| Python 3.10 trở lên | `build.py`, `check_site.py`, `make_thumbs.py` | Máy hiện tại chạy 3.10.11. `build.py` và `check_site.py` chỉ dùng thư viện chuẩn. |
| Pillow | `make_thumbs.py` | `pip install Pillow` (đang dùng 12.2.0). Chỉ cần khi có bài mới thiếu ảnh. |
| Git | Lưu phiên bản, đẩy lên GitHub | |
| Trình duyệt | Xem thử | Bất kỳ trình duyệt hiện đại nào |

Không cần Node.js, npm hay cơ sở dữ liệu.

`check_site.py` kiểm tra cú pháp code Python mẫu bằng chính trình thông dịch đang chạy. Với Python 3.10,
code mẫu dùng cú pháp 3.11+ (generic `def f[T]()`, f-string lồng cùng loại nháy) sẽ bị báo lỗi dù chạy
đúng trên bản mới. Xem [04. Viết bài](04-viet-bai.md#code-mẫu).

## Lấy mã nguồn

```bash
git clone https://github.com/dbh92/Portfolio.git
cd Portfolio
pip install Pillow        # tùy chọn, chỉ để vẽ ảnh đại diện
```

Repo hiện có hai remote: `origin` → `dbh92/BlogMe` và `portfolio` → `dbh92/Portfolio`. Kiểm tra bằng
`git remote -v` và đẩy lên remote đang được GitHub Pages phục vụ.

## Ba lệnh chính

### `python tools/make_thumbs.py`

Vẽ ảnh đại diện 1200×675 cho bài nào trong `src/posts.json` chưa có `assets/images/posts/<slug>.jpg`.
Mỗi bài có hai file:

- `<slug>.webp` (chất lượng 80): hiển thị trên trang, nhẹ.
- `<slug>.jpg` (chất lượng 86, progressive): dùng cho `og:image`, JSON-LD, chia sẻ mạng xã hội.

Tùy chọn:

| Lệnh | Tác dụng |
|---|---|
| `python tools/make_thumbs.py` | Chỉ vẽ ảnh còn thiếu. Nếu có `.jpg` mà thiếu `.webp`, tạo `.webp` từ `.jpg`. |
| `python tools/make_thumbs.py --all` | Vẽ lại **toàn bộ** ảnh, kể cả ghi đè ảnh thật bạn đã chép vào. Cẩn thận. |

Script cũng vẽ `assets/images/og-default.jpg` (ảnh chia sẻ mặc định) nếu file chưa có. Cách ảnh được vẽ
và cách dùng ảnh thật: xem [04. Viết bài](04-viet-bai.md#ảnh-đại-diện).

### `python tools/build.py`

Sinh lại **toàn bộ** site từ `src/`. Không có build từng phần: mỗi lần chạy ghi đè mọi trang. Thời gian
chạy vài giây. Kết thúc bằng dòng:

```
Xong: 388 bài viết, 59 chủ đề, 4 lộ trình.
```

Lưu ý khi build:

- Nếu dữ liệu sai, build dừng ở một `AssertionError` có thông báo tiếng Việt **trước khi ghi file nào**.
  Danh sách các kiểm tra ở [06. Bên trong build.py](06-build-py.md#các-kiểm-tra-khi-nạp-dữ-liệu).
- CSS và JS được gắn `?v=YYYYMMDD` theo ngày build để trình duyệt tải bản mới. Vì vậy build vào một ngày
  mới làm **mọi trang** đổi một dòng. Diff đó là bình thường, cứ commit.
- `sitemap.xml` ghi `lastmod` là ngày build cho các trang không phải bài viết; bài viết dùng `date` của bài.
- Năm trong chân trang (`© 2026 HọcFree.vn`) lấy theo năm hiện tại.

### `python tools/check_site.py`

Kiểm tra site đã build. In số trang, số bài, số khối code Python, rồi `OK: không có lỗi` (mã thoát 0)
hoặc danh sách tối đa 80 lỗi (mã thoát 1). Chi tiết từng kiểm tra ở
[08. Kiểm tra và xử lý lỗi](08-kiem-tra-xu-ly-loi.md).

**Luôn chạy sau mỗi lần build, trước khi commit.**

## Xem thử trên máy

```bash
python -m http.server 8000
```

Mở <http://localhost:8000>. Nên xem qua máy chủ thay vì mở file trực tiếp (`file://`) vì:

- Trang 404 dùng đường dẫn tuyệt đối `/…`, chỉ đúng khi có máy chủ.
- `navigator.clipboard` (nút "Sao chép") chỉ chạy trong ngữ cảnh an toàn; `localhost` được tính là an toàn.

Những trang cần xem lại sau khi sửa: trang chủ, một trang chủ đề, bài vừa viết (cả chế độ sáng và tối,
cả màn hình hẹp dưới 640px), hộp tìm kiếm `Ctrl K` với một từ khóa trong bài mới.

## Commit

- Commit **cả nguồn lẫn file sinh ra** trong cùng một commit. GitHub Pages không chạy build; nó phục vụ
  đúng những gì có trong nhánh.
- Commit message bằng tiếng Việt có dấu, mô tả nội dung, ví dụ:
  `Thêm bài: hiệu chuẩn camera bằng bàn cờ`, `Lộ trình Python Developer: 10 chặng, 53 bài học…`.
- `.gitignore` đã loại `__pycache__/`, `*.pyc`, `.DS_Store`, `Thumbs.db`, `.vscode/`.

## Triển khai lên GitHub Pages

Site được phục vụ từ **thư mục gốc của nhánh `main`**. Không có GitHub Actions; đẩy lên `main` là đăng.

- `.nojekyll` (file rỗng) tắt Jekyll để GitHub phục vụ nguyên trạng mọi file.
- `404.html` ở gốc được GitHub Pages trả về cho mọi đường dẫn không tồn tại.
- Thiết lập trong GitHub: repo → **Settings → Pages** → Source: *Deploy from a branch*, Branch: `main`,
  thư mục `/ (root)`.

### Tên miền hocfree.vn

Tên miền mua tại Mắt Bão nhưng nameserver là Cloudflare, nên bản ghi DNS khai trong Cloudflare
(chi tiết trong [`../README.md`](../README.md#trỏ-tên-miền--github-pages)):

| Loại | Name | Giá trị | Proxy |
|---|---|---|---|
| A | @ | 185.199.108.153 / .109.153 / .110.153 / .111.153 | DNS only |
| CNAME | www | dbh92.github.io | DNS only |

Sau đó vào Settings → Pages → Custom domain `hocfree.vn`, bật **Enforce HTTPS**.

> **Trạng thái ngày 05/11/2026:** file `CNAME` không còn trong repo (commit `5d31a5a Delete CNAME`, sau
> chuỗi xóa/tạo lại). Với Pages kiểu "deploy from a branch", GitHub lưu tên miền riêng trong file `CNAME`
> ở gốc nhánh. Nếu hocfree.vn cần trỏ về repo này, tạo lại `CNAME` chứa đúng một dòng `hocfree.vn`
> (hoặc nhập lại trong Settings → Pages, GitHub sẽ tự commit file).

Mọi URL tuyệt đối trong trang (canonical, `og:url`, sitemap, JSON-LD) lấy từ `site.domain` trong
`src/posts.json` (`https://hocfree.vn`). Đổi tên miền thì sửa trường đó rồi build lại.

## Quy trình theo tình huống

### Thêm một bài viết

1. Thêm một dòng vào mảng `posts` trong `src/posts.json` ([03. Dữ liệu nguồn](03-du-lieu-nguon.md#bài-viết-posts)).
2. Viết `src/posts/<slug>.html` ([04. Viết bài](04-viet-bai.md)).
3. `python tools/make_thumbs.py` → `python tools/build.py` → `python tools/check_site.py`.
4. Xem thử, commit, push.

### Sửa một bài đã đăng

Sửa `src/posts/<slug>.html` hoặc dòng của bài trong `src/posts.json`, rồi build và kiểm tra. Nếu muốn
báo cho máy tìm kiếm là bài đã cập nhật, thêm trường `"updated": "YYYY-MM-DD"` (đi vào `dateModified`).
**Không đổi `slug`** của bài đã đăng: URL sẽ đổi, link từ ngoài vào sẽ thành 404.

### Thêm chủ đề vào menu

Thêm một item vào nhóm phù hợp trong `src/nav.json`, đặt `tags` để gom bài. Chủ đề chưa có bài vẫn được
tạo trang, hiện "Đang biên soạn", đặt `noindex` và không vào sitemap.

### Thêm lộ trình hoặc bài học

Xem [05. Learning Paths và bài học](05-lo-trinh-hoc.md).

### Đổi link tải tài liệu (Google Drive)

Sửa `downloads.<key>.url` trong `src/posts.json`, đặt `"ready": true` khi link đã mở được, rồi build.
Mọi bài dùng `{{download:<key>}}` tự cập nhật.

### Xóa một bài

1. Xóa dòng của bài trong `src/posts.json` và file `src/posts/<slug>.html`.
2. Gỡ slug khỏi `popular`, khỏi `lessons`/`extras` trong `src/learning-paths.json` nếu có (build sẽ báo
   nếu `extras` còn trỏ tới slug đã xóa; slug trong `lessons` thì tự chuyển thành "Đang biên soạn").
3. Tìm link tới bài từ các bài khác: `grep -rn "<slug>.html" src/posts/`.
4. Xóa file sinh ra `<chuyên-mục>/<slug>.html` (build **không** tự xóa trang cũ) và ảnh trong
   `assets/images/posts/`.
5. Build, kiểm tra. `check_site.py` sẽ bắt link hỏng còn sót trong các trang khác.

### Đổi tên hoặc xóa chủ đề, chặng

Tương tự xóa bài: build không dọn file cũ. Sau khi đổi slug, xóa trang HTML cũ bằng tay
(`git rm <mục>/<chủ-đề-cũ>.html`), cập nhật mọi `topics` trong `learning-paths.json` và `popularTopics`
trong `nav.json` đang trỏ tới slug cũ.
