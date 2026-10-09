# Quy trình đăng bài tự động hằng ngày

Routine **"HọcFree – đăng 10 bài lúc 5h"** mở một phiên Claude Code mới mỗi đêm (10/10 → 29/10/2026).
Phiên đó làm đúng các bước dưới đây. Sửa file này để đổi quy tắc, không cần tạo lại Routine.

## 0. Xác định ngày

```bash
TODAY=$(TZ=Asia/Ho_Chi_Minh date +%F)
```

Mở `src/editorial-plan.json`, tìm phần tử trong `days` có `date == TODAY`.

- Không có, hoặc `status` đã là `published`: **dừng**, không sửa gì, báo lại lý do.
- Có và `status == "pending"`: làm tiếp với 10 chủ đề trong `topics` của ngày đó.

## 1. Nhánh làm việc

```bash
git fetch origin main
git checkout -B <nhánh> origin/main
```

Dùng nhánh mà hướng dẫn phiên chỉ định; nếu không có, đặt tên `auto/bai-viet-$TODAY`.

## 2. Viết 10 bài (mỗi chủ đề 1 bài)

Với mỗi `ref` trong `topics` của ngày (ví dụ `hoc/opencv`), tra `topics[ref]` ở đầu file kế hoạch để có
`category`, `menu`, `tags`.

1. **Chọn đề tài mới**: liệt kê các bài hiện có thuộc chủ đề (bài có tag trùng một tag của chủ đề trong
   `src/posts.json`), chọn đề tài **không trùng** và hữu ích cho người học, ưu tiên kiến thức thực tế cho
   kỹ sư AI / Computer Vision / Machine Vision người Việt.
2. **Tra cứu** bằng WebSearch để kiểm tra phiên bản thư viện, tên hàm, tham số, số liệu. Không bịa số liệu,
   tên sản phẩm, trích dẫn. Không chắc thì không viết chi tiết đó.
3. **Chủ đề Tin tức AI** (`tin-tuc-ai/*`): chỉ viết về sự kiện **có thật** trong khoảng 10 ngày trước `TODAY`,
   kiểm tra ở ít nhất 2 nguồn nếu có thể, ghi rõ nguồn. Không xác minh được thì chọn tin khác.
4. **Thân bài**: lưu ở `src/posts/<slug>.html`, chỉ là đoạn HTML (không `<html>`, `<head>`, `<h1>`).
   - Dùng `<p>`, `<h2>`, `<h3>`, `<ul>/<ol>`, `<table>`, `<blockquote>`, `<pre><code>`; không style nội tuyến,
     không script.
   - Trong `<pre><code>` phải escape `&lt;`, `&gt;`, `&amp;`.
   - Dài khoảng 700–1500 từ, tiếng Việt có dấu đầy đủ, câu ngắn, dễ hiểu, có ví dụ thực tế.
   - Code chạy được: đủ import, đúng cú pháp, API đúng phiên bản hiện hành.
   - Link sang bài liên quan đã có: cùng mục dùng `slug.html`, khác mục dùng `../<category>/slug.html`.
   - Có dữ kiện bên ngoài thì kết bài bằng `<p class="note">Nguồn tham khảo: <a href="…" rel="noopener" target="_blank">…</a></p>`
     với URL thật đã tìm được.
5. **Thông tin bài**: thêm vào mảng `posts` của `src/posts.json` (giữ định dạng mỗi bài một dòng, dùng script
   Python với `json.dumps(..., ensure_ascii=False)`):

   ```json
   {"slug": "…", "category": "<topics[ref].category>", "title": "…", "excerpt": "…", "date": "<TODAY>",
    "tags": ["<tag chính của chủ đề>", "…"], "thumb": {"glyph": "…", "colors": ["#rrggbb", "#rrggbb"]}}
   ```

   - `slug`: chữ thường không dấu, nối bằng `-`, duy nhất, không trùng slug chủ đề trong `src/nav.json`.
   - `tags`: **phải có ít nhất một tag của chủ đề** (để bài hiện trong menu đó), thêm 1–3 tag có sẵn liên quan.
   - `title` nên ≤ 70 ký tự; `excerpt` 120–170 ký tự.
   - `thumb.glyph`: 2–6 ký tự ngắn gọn (ví dụ `YOLO`, `cv2`, `PLC`); `colors`: màu sáng rồi màu tối, cùng tông.

## 3. Cập nhật kế hoạch

Trong `src/editorial-plan.json`, ngày `TODAY`: `"status": "published"`, `"posts": [<10 slug>]`.

## 4. Build và kiểm tra

```bash
python3 tools/make_thumbs.py
python3 tools/build.py
python3 tools/check_site.py      # phải in "OK: không có lỗi"
```

Sửa mọi lỗi rồi chạy lại cho tới khi OK. Không sửa file nào ngoài: `src/posts.json`, `src/posts/*.html`,
`src/editorial-plan.json`, ảnh trong `assets/images/posts/` và các file HTML do `build.py` sinh ra.
Không xóa hay sửa bài cũ.

## 5. Commit, PR, đăng lúc 5h

1. Commit: `Đăng 10 bài ngày DD/MM/YYYY (ngày N/20)`, kèm dòng ghi công theo hướng dẫn của phiên. Push nhánh.
2. Tạo PR vào `main` (repo `dbh92/portfolio`), nội dung liệt kê 10 bài: tiêu đề, menu, đường dẫn.
3. **Chờ đến 05:00 giờ Việt Nam** nếu còn sớm (chạy nền, đợi lệnh kết thúc rồi làm tiếp):

   ```bash
   until [ "$(TZ=Asia/Ho_Chi_Minh date +%H%M)" -ge 0500 ]; do sleep 30; done
   ```

4. Merge PR (kiểu `merge`). Nếu main đã thay đổi gây xung đột: merge `origin/main` vào nhánh, build và
   kiểm tra lại, push, rồi merge.
5. **Không có công cụ GitHub để tạo/merge PR** (không thấy `mcp__github__*`): bỏ qua bước tạo PR, đến 05:00 thì
   merge bằng git rồi đẩy thẳng lên main:

   ```bash
   git fetch origin main
   git checkout -B main origin/main
   git merge --no-ff <nhánh> -m "Đăng 10 bài ngày DD/MM/YYYY (ngày N/20)"
   python3 tools/build.py && python3 tools/check_site.py   # phải OK
   git push origin main
   ```

   Nếu `git push` bị từ chối, báo rõ lỗi (nhánh bài viết vẫn nằm trên remote để chủ site gộp tay).
6. Nếu không sửa được lỗi kiểm tra: **không merge**, để PR/nhánh mở và báo rõ lỗi.

## 6. Báo cáo

Tóm tắt: ngày thứ mấy/20, 10 bài đã đăng (tiêu đề + menu), link PR, vấn đề gặp phải (nếu có).
