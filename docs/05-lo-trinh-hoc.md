# 05. Learning Paths và bài học

Learning Path (lộ trình) là phần "Bước 3 · Trở thành kỹ sư" của site: một chuỗi chặng có thứ tự, mỗi chặng
là một danh sách bài học có mục tiêu, bài tập và dự án. Toàn bộ khai báo trong `src/learning-paths.json`;
bảng trường đầy đủ ở [03. Dữ liệu nguồn](03-du-lieu-nguon.md#srclearning-pathsjson).

## Cấu trúc

```
Lộ trình (path)              lo-trinh/<path>.html
└── Giai đoạn (phase)        nhóm các chặng trên bản đồ lộ trình
    └── Chặng (step)         lo-trinh/<path>/<step>.html
        ├── topics           liên kết hai chiều với trang chủ đề trong nav.json
        ├── lessons          bài học theo đúng thứ tự (lesson / lab / project)
        └── extras           bài đọc thêm, không bắt buộc
```

Ngày 05/11/2026:

| Lộ trình | Giai đoạn | Chặng | Bài học khai báo |
|---|---|---|---|
| `vision-engineer` ⭐ | `nen-tang`, `machine-vision`, `tich-hop`, `ai-vision`, `thuc-chien` | 15 | 123 |
| `python-developer` | `nen-tang`, `chuyen-nghiep`, `ung-dung`, `trien-khai` | 10 | 53 (slug tiền tố `pydev-`) |
| `toeic-700` | `thang-1` … `thang-5` | 11 | 60 |
| `hsk3` | `gd-1` … `gd-5` | 10 | 61 |

## Các trang được sinh

### `lo-trinh/` (danh sách lộ trình)

Thẻ lớn cho lộ trình flagship, thẻ cho các lộ trình khác đã có chặng, và lưới "Lộ trình khác" cho lộ trình
chưa có `steps` (huy hiệu "Sắp ra mắt").

### `lo-trinh/<path>.html` (bản đồ lộ trình)

- Đầu trang: tên, tagline, mô tả, số chặng, số giai đoạn, thời lượng, tổng số tuần (cộng `weeks`).
- "Bạn đang ở đâu?": các `entryPoints`, mỗi thẻ nhảy tới chặng tương ứng.
- Bản đồ bên trái (giai đoạn → chặng) kèm thanh tiến độ "N/M chặng".
- Mỗi chặng: "Bạn sẽ học", "Học xong bạn có thể", danh sách bài học thu gọn kèm số bài đã học, nút
  "Vào học chặng N", ô "Đã hoàn thành chặng".
- Cuối trang: khối đích đến (`goal`) với anchor `#muc-tieu`.
- JSON-LD `Course` với mỗi chặng là một `hasPart`.

### `lo-trinh/<path>/<step>.html` (trang chặng)

- Kicker "Giai đoạn N · … · Chặng N/M", tiêu đề, `outcome`, số bài, số giờ (tổng `min` / 60, làm tròn),
  số tuần, số bài đã học.
- Nút "Bắt đầu bài 1": sau khi người học đã đánh dấu ít nhất một bài, nút đổi thành "Học tiếp: <bài chưa học
  đầu tiên>"; học hết thì thành "Đã học hết chặng này ✓ Ôn lại".
- "Trước khi bắt đầu" (`before`) và "Chặng này gồm" (`learn`).
- Giáo trình: mỗi bài có số thứ tự, tên, mục tiêu, loại, số phút, ô đánh dấu đã học. Bài chưa viết hiện
  "Đang biên soạn".
- "Đọc thêm" từ `extras`, điều hướng chặng trước/sau, sidebar tiến độ và bản đồ các chặng.

`lo-trinh/<path>/index.html` là trang chuyển hướng (meta refresh, `noindex`) về `lo-trinh/<path>.html`, để
URL thư mục không bị 404.

### Trang bài học

Bài viết có slug nằm trong `lessons` được dựng thành trang bài học (vẫn ở `/<category>/<slug>.html`):

| Thành phần | Nguồn |
|---|---|
| Breadcrumb Trang chủ / Learning Paths / lộ trình / chặng | `path.short`, `step.title` |
| Thanh khóa học: "⭐ <short> · Chặng N", "Bài i/n", loại bài, "~min phút" | `lessons[i]` |
| "Học xong bài này, bạn sẽ" + "Nên học trước: <bài trước>" | `goals`, thứ tự giáo trình |
| Thân bài | `src/posts/<slug>.html` |
| "Bài tập thực hành" + câu nhắc | `practice`, `path.practiceNote` |
| Nút "Đánh dấu đã học xong", nút "Bài tiếp theo" (bài cuối: "Xem đích đến 🎯") | thứ tự giáo trình |
| Nút bài trước/sau (thay cho bài trước/sau theo ngày) | thứ tự giáo trình, xuyên qua các chặng |
| Sidebar: mục lục chặng có tiến độ (thay cho sidebar thường) | `step.lessons` |
| Mục menu "Learning Paths" được tô sáng | |
| JSON-LD Article có `isPartOf: Course` | |

"Thứ tự giáo trình" là danh sách các bài **đã viết** của lộ trình, đi lần lượt qua các chặng. Bài chưa viết
bị bỏ qua khi tính bài trước/sau, nên bài cuối chặng 1 trỏ thẳng tới bài viết đầu tiên có của chặng 2.

## Liên kết với trang chủ đề

`topics` của chặng nối chặng với chủ đề trong `nav.json`:

- Trang chủ đề có widget "Có trong lộ trình" liệt kê mọi chặng nhắc tới nó.
- Trong các chặng nhắc tới chủ đề, chặng đầu tiên có `lessons` làm trang chủ đề hiện banner "⭐ Mới bắt đầu? Học theo
  thứ tự" với nút "Bắt đầu bài 1", và sắp bài trên trang chủ đề theo thứ tự giáo trình (bài không thuộc
  giáo trình xếp sau, theo ngày).
- Chủ đề chưa có bài hiện nút "Xem chặng này trong lộ trình".

## Tiến độ người học

Không có tài khoản; tiến độ lưu trong `localStorage` của trình duyệt (xóa dữ liệu trình duyệt là mất):

| Khóa | Giá trị | Ghi bởi |
|---|---|---|
| `hf-path-<path>` | Mảng slug chặng đã đánh dấu "Đã hoàn thành chặng" | Ô đánh dấu trên trang lộ trình |
| `hf-lessons-<path>` | Mảng slug bài đã học | Ô đánh dấu trên trang chặng, nút "Đánh dấu đã học xong" trên trang bài học |

Hai loại tiến độ độc lập: học xong mọi bài của chặng **không** tự đánh dấu chặng hoàn thành.

Vì khóa gắn với slug, **đổi slug lộ trình, chặng hoặc bài học làm mất tiến độ đã lưu** của người học.

## Thêm hoặc sửa lộ trình

### Thêm bài học vào chặng có sẵn

1. Thêm một phần tử vào `lessons` của chặng, đúng vị trí trong thứ tự học:

   ```json
   {
     "slug": "opencv-8-hieu-chuan-camera",
     "kind": "lesson",
     "min": 60,
     "title": "Hiệu chuẩn camera bằng bàn cờ",
     "goals": ["Hiểu ma trận nội K và hệ số méo", "Chạy calibrateCamera và đọc sai số tái chiếu"],
     "practice": ["Hiệu chuẩn webcam của bạn với 15 ảnh bàn cờ, ghi lại RMS."]
   }
   ```

2. Build ngay được: bài chưa viết hiện "Đang biên soạn".
3. Khi viết bài, thêm bài vào `posts.json` với **đúng slug đó** và tạo thân bài như mọi bài khác
   ([04. Viết bài](04-viet-bai.md)). Trang bài học tự xuất hiện.

Ràng buộc: một slug chỉ được là bài học của **một** chặng trong toàn bộ các lộ trình (build báo
`Bài … nằm trong hai chặng`). Muốn dùng một bài ở lộ trình thứ hai, đặt nó vào `extras` của chặng đó, hoặc
viết bài riêng như lộ trình Python Developer đã làm (bài `pydev-*` thay vì dùng lại bài Python của Vision
Engineer).

### Thêm chặng

Thêm phần tử vào `steps` (đúng vị trí), với `phase` là một `slug` trong `phases`, `topics` là các `ref` có
thật trong `nav.json`, `extras` là slug bài có thật. Số thứ tự chặng tính theo vị trí, không khai báo.

### Thêm lộ trình mới

1. Thêm một phần tử vào `paths`. Có thể bắt đầu chỉ với `slug`, `label`, `short`, `tagline`, `description`
   (không có `steps`): lộ trình hiện "Sắp ra mắt" trong menu và trang `lo-trinh/`.
2. Khi có nội dung, bổ sung `duration`, `pace`, `preview`, `entryPoints`, `phases`, `goal`, `steps`.
3. Muốn lộ trình hiện thành thẻ lớn trên trang hub của một mục, thêm slug vào `featured` của mục đó trong
   `nav.json` (ví dụ mục `hoc` có `["vision-engineer", "python-developer"]`, `ngoai-ngu` có
   `["toeic-700", "hsk3"]`).
4. Build, kiểm tra, xem thử trang lộ trình, một trang chặng, một trang bài học.

Không đặt `flagship: true` cho lộ trình thứ hai: trang chủ và hộp tìm kiếm chỉ dùng lộ trình flagship đầu
tiên, còn lộ trình flagship thứ hai sẽ không có thẻ trên trang `lo-trinh/`.

## Gợi ý biên soạn giáo trình

- `goals` 2–4 ý, bắt đầu bằng động từ đo được ("Tính", "Viết", "Phân biệt"), không phải "Hiểu về…".
- `practice` là việc người học tự làm, có kết quả kiểm tra được.
- `min` là thời gian học thật, gồm cả làm bài tập; tổng của chặng nên khớp với `weeks` và `pace`.
- Mỗi chặng kết bằng một bài `lab` hoặc `project` tổng hợp kiến thức chặng.
- `before` nói rõ điều kiện đầu vào; `outcome` nói rõ đầu ra, viết thành câu "Học xong bạn có thể…".
