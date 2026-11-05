# Tài liệu dự án HọcFree.vn

Bộ tài liệu dành cho người duy trì và người viết bài cho HọcFree: website tĩnh tiếng Việt dạy AI,
Computer Vision, Machine Vision, lập trình và ngoại ngữ, chạy trên GitHub Pages.

Cập nhật lần cuối: 05/11/2026 (388 bài viết, 59 chủ đề, 4 lộ trình, 513 trang HTML).

## Đọc theo nhu cầu

| Bạn muốn | Đọc |
|---|---|
| Hiểu dự án là gì, chạy thế nào, file nào làm gì | [01. Tổng quan và kiến trúc](01-tong-quan-kien-truc.md) |
| Cài môi trường, build, xem thử, đưa lên mạng | [02. Cài đặt, build và triển khai](02-cai-dat-build-trien-khai.md) |
| Tra cứu từng trường trong `src/*.json` | [03. Dữ liệu nguồn](03-du-lieu-nguon.md) |
| Viết hoặc sửa một bài viết | [04. Hướng dẫn viết bài](04-viet-bai.md) |
| Thêm lộ trình, chặng, bài học | [05. Learning Paths và bài học](05-lo-trinh-hoc.md) |
| Sửa trình sinh trang `tools/build.py` | [06. Bên trong build.py](06-build-py.md) |
| Sửa giao diện, CSS, JavaScript | [07. Giao diện và JavaScript](07-giao-dien-javascript.md) |
| Build hoặc kiểm tra báo lỗi | [08. Kiểm tra và xử lý lỗi](08-kiem-tra-xu-ly-loi.md) |
| Chạy quy trình đăng bài tự động | [auto-publish.md](auto-publish.md) |

## Ba quy tắc không được quên

1. **Không sửa tay file sinh ra.** Mọi `.html` ở gốc và trong `hoc/ projects/ lo-trinh/ kien-thuc/
   tin-tuc-ai/ ngoai-ngu/ tai-nguyen/`, cùng `assets/js/search-data.js`, `sitemap.xml`, `robots.txt`
   đều do `tools/build.py` ghi đè. Sửa nguồn trong `src/` rồi build lại.
2. **Build xong phải kiểm tra.** `python tools/check_site.py` phải in `OK: không có lỗi`.
3. **Tiếng Việt có dấu đầy đủ** trong nội dung, chú thích code và commit message.

## Chu trình làm việc ngắn gọn

```bash
# sửa src/posts.json, src/posts/<slug>.html, src/nav.json, src/learning-paths.json…
python tools/make_thumbs.py     # vẽ ảnh đại diện còn thiếu
python tools/build.py           # sinh lại toàn bộ trang
python tools/check_site.py      # phải in "OK: không có lỗi"
python -m http.server 8000      # xem thử tại http://localhost:8000
git add -A && git commit -m "Thêm bài …" && git push
```

Trên Windows, nếu terminal báo `UnicodeEncodeError`, chạy `python -X utf8 tools/…` (xem
[mục 08](08-kiem-tra-xu-ly-loi.md), phần "Lỗi khi chạy công cụ").

## Tài liệu khác trong repo

- [`../README.md`](../README.md): giới thiệu ngắn, cấu hình DNS cho tên miền.
- [`../CLAUDE.md`](../CLAUDE.md): hướng dẫn rút gọn cho Claude Code khi làm việc trong repo.
- Các trường `_doc` trong `src/nav.json`, `src/learning-paths.json`, `src/editorial-plan.json`,
  `src/posts.json`: ghi chú ngay tại chỗ dữ liệu.
