# 03. Dữ liệu nguồn

Tra cứu từng trường trong các file `src/*.json`: ý nghĩa, bắt buộc hay không, dùng ở đâu, ràng buộc.
Mọi file là UTF-8, giữ nguyên tiếng Việt có dấu (khi ghi bằng Python dùng `ensure_ascii=False`).
Trường bắt đầu bằng `_` (ví dụ `_doc`) là ghi chú, `build.py` bỏ qua.

## `src/posts.json`

```json
{
  "site": { … },
  "downloads": { … },
  "popular": [ … ],
  "posts": [
    {"slug": "…", "category": "…", …},
    {"slug": "…", "category": "…", …}
  ]
}
```

**Quy ước định dạng:** mảng `posts` giữ **mỗi bài một dòng** để diff gọn và dễ gộp nhánh. Khi sửa bằng
script, ghi từng phần tử bằng `json.dumps(p, ensure_ascii=False)`, đừng `json.dump(..., indent=2)` cả file.
Thứ tự các dòng không quan trọng: `build.py` tự sắp bài theo `date` giảm dần (bài cùng ngày giữ thứ tự
trong file).

### `site`

| Trường | Ví dụ | Dùng ở |
|---|---|---|
| `name` | `HọcFree` | `<title>`, `og:site_name`, JSON-LD Organization, logo |
| `domain` | `https://hocfree.vn` | Mọi URL tuyệt đối: canonical, `og:url`, `og:image`, sitemap, robots, JSON-LD, nút chia sẻ. **Không có `/` ở cuối.** |
| `tagline` | `Học AI, lập trình & Computer Vision miễn phí` | Tiêu đề trang chủ: `HọcFree – <tagline>` |
| `description` | `HọcFree.vn – nền tảng học miễn phí…` | Meta description trang chủ, chân trang |
| `author` | `Ban biên tập HọcFree` | Dòng tác giả trong bài, hộp tác giả, JSON-LD `author` |

### `downloads`

Link tải tài liệu (thường là thư mục Google Drive), khai báo một chỗ để nhiều bài dùng chung.

```json
"hf-700toeic": {
  "label": "HF-700TOEIC",
  "desc": "Bộ giáo trình tự học 700 TOEIC trên Google Drive (miễn phí)",
  "cta": "Mở Google Drive",
  "url": "https://drive.google.com/drive/folders/…",
  "ready": false
}
```

| Trường | Bắt buộc | Ý nghĩa |
|---|---|---|
| khóa (`hf-700toeic`) | có | Tên dùng trong bài: `{{download:hf-700toeic}}`. Chỉ chữ, số, `_`, `-`. |
| `label` | có | Tiêu đề in đậm trong hộp tải |
| `desc` | có | Dòng mô tả |
| `url` | có | Link mở khi bấm nút (tab mới, `rel="noopener"`) |
| `cta` | không | Chữ trên nút, mặc định `Mở Google Drive` |
| `ready` | không | `false` hoặc thiếu: thêm ghi chú "Bộ tài liệu đang được hoàn thiện…". `true`: bỏ ghi chú. |

Ngày 05/11/2026 có hai khóa `hf-700toeic` và `hf-hsk3`, cả hai `ready: false` với URL giữ chỗ.

### `popular`

Danh sách slug cho widget "Đọc nhiều nhất" ở sidebar. Hiện tối đa 5 bài đầu tiên **có tồn tại**, bỏ bài
đang xem. Slug không còn tồn tại bị bỏ qua lặng lẽ (không báo lỗi). Không có số liệu lượt xem: danh sách
này do người biên tập tự chọn.

### Bài viết (`posts`)

```json
{"slug": "opencv-co-ban-anh-video-camera", "category": "hoc", "title": "…", "excerpt": "…", "date": "2026-10-05", "tags": ["OpenCV", "Python"], "thumb": {"glyph": "cv2", "colors": ["#22c55e", "#052e16"]}}
```

| Trường | Bắt buộc | Ràng buộc | Dùng ở |
|---|---|---|---|
| `slug` | có | Chữ thường không dấu, số, `-`. Duy nhất trong mọi bài. Không trùng URL một trang chủ đề cùng mục. **Không đổi sau khi đăng.** | URL `<category>/<slug>.html`, tên file thân bài và ảnh |
| `category` | có | Một trong `hoc`, `projects`, `kien-thuc`, `tin-tuc-ai`, `ngoai-ngu`, `tai-nguyen` (các mục có `groups` trong `nav.json`) | Thư mục chứa bài, nhãn chuyên mục, breadcrumb, mục menu được tô sáng |
| `title` | có | Nên ≤ 70 ký tự. Từ 59 ký tự trở lên, `<title>` không kèm hậu tố ` \| HọcFree` | `<h1>`, `<title>`, `og:title`, thẻ bài, tìm kiếm |
| `excerpt` | có | 120–170 ký tự, một câu tóm tắt có nội dung (không phải "Bài này nói về…") | Meta description, đoạn dẫn dưới `<h1>`, danh sách bài, tìm kiếm |
| `date` | có | `YYYY-MM-DD` | Sắp xếp, ngày hiển thị (`DD/MM/YYYY`), `datePublished`, `lastmod` trong sitemap, nút bài trước/sau |
| `tags` | có | Mảng chuỗi. Phải chứa ít nhất một tag của chủ đề muốn bài xuất hiện. Dùng lại tag có sẵn, viết đúng hoa/thường như nơi khác dù so khớp không phân biệt hoa thường. | Trang chủ đề, mây thẻ ở sidebar (link `search.html?q=<tag>`), `article:tag`, `keywords`, tìm kiếm |
| `thumb.glyph` | có | 2–6 ký tự ngắn, ví dụ `YOLO`, `cv2`, `PLC`, `HSK 3.0`. Chữ Hán và ký hiệu được hỗ trợ (xem [04](04-viet-bai.md#ảnh-đại-diện)). | Chữ lớn trên ảnh đại diện tự vẽ |
| `thumb.colors` | có | `["#màu-sáng", "#màu-tối"]`, cùng tông | Màu quầng sáng và nền ảnh đại diện |
| `math` | không | `true` để tải KaTeX | Bài có công thức `\( … \)`, `\[ … \]` |
| `updated` | không | `YYYY-MM-DD` | JSON-LD `dateModified` (mặc định bằng `date`) |

Mỗi bài cần đủ ba file: `src/posts/<slug>.html`, `assets/images/posts/<slug>.jpg`,
`assets/images/posts/<slug>.webp`. Thiếu thân bài thì `build.py` dừng; thiếu ảnh thì `check_site.py` báo lỗi.

Các trường `build.py` tự tính, **không khai trong JSON**: `body` (thân bài đã chèn hộp tải), `minutes`
(thời gian đọc ≈ số từ / 180, làm tròn lên, tối thiểu 1), `cat` (thông tin chuyên mục).

## `src/nav.json`

```json
{
  "sections": [ {mục}, {mục}, … ],
  "popularTopics": ["hoc/python", "hoc/opencv", …]
}
```

Thứ tự trong `sections` là thứ tự trên menu.

### Mục (`sections[]`)

| Trường | Ý nghĩa |
|---|---|
| `key` | Mã nội bộ, duy nhất. `build.py` tham chiếu trực tiếp các khóa `home`, `hoc`, `projects`, `lo-trinh`, `kien-thuc`, `tin-tuc-ai`, `ngoai-ngu`, `tai-nguyen` khi dựng trang chủ, nên **đừng đổi tên các khóa này**. |
| `label` | Tên hiển thị trên menu, breadcrumb, tiêu đề trang hub; cũng là tên chuyên mục của bài |
| `slug` | Tên thư mục (`hoc` → `hoc/`). Với mục có `groups`, đây chính là giá trị `category` của bài. |
| `href` | Chỉ cho mục là một link đơn (ví dụ `home` → `index.html`). Mục có `href` và không có `groups`/`layout` hiện là link thường. |
| `layout` | `mega`: mega menu nhiều cột kèm thẻ lộ trình nổi bật (cần `featured`). `paths`: dropdown liệt kê mọi lộ trình. Bỏ trống: dropdown thường, một hoặc nhiều cột nhóm. |
| `step`, `stepLabel`, `stepDesc` | Đánh dấu mục thuộc hành trình 3 bước (dải "Học → Thực hành → Trở thành kỹ sư"), hiện kicker "Bước N · …" trên panel menu và trang hub, cột "Học & thực hành" ở chân trang |
| `description` | Mô tả trên trang hub, meta description, danh sách ở trang Giới thiệu |
| `featured` | Một slug hoặc mảng slug lộ trình. Hiện thẻ lộ trình lớn trên trang hub; lộ trình đầu tiên hiện trong mega menu. |
| `align` | `end`: panel dropdown canh theo mép phải (cho mục ở cuối menu) |
| `groups` | Danh sách nhóm chủ đề. **Mục có `groups` là một chuyên mục**: có trang hub `<slug>/index.html` và có thể chứa bài. |

Mục `lo-trinh` không có `groups`: nó không chứa bài; trang `lo-trinh/` do `build_paths_index` dựng.

### Nhóm (`groups[]`)

| Trường | Ý nghĩa |
|---|---|
| `slug` | Id của khối nhóm trên trang hub (`hoc/#computer-vision`). Chỉ có anchor khi mục có từ 2 nhóm. |
| `label` | Tiêu đề nhóm trên menu, trang hub, sidebar trang chủ đề |
| `items` | Danh sách chủ đề |

### Chủ đề (`items[]`)

```json
{ "slug": "object-detection", "label": "Object Detection", "tags": ["Object Detection", "YOLO"] }
```

| Trường | Bắt buộc | Ý nghĩa |
|---|---|---|
| `slug` | có | Trang `<mục>/<slug>.html`. Duy nhất trong mục; không trùng slug bài cùng thư mục. Tham chiếu ở nơi khác bằng `ref` = `<mục>/<slug>` (ví dụ `hoc/opencv`). |
| `label` | có | Tên chủ đề |
| `tags` | gần như luôn | Bài có **ít nhất một** tag trùng (không phân biệt hoa thường) thì thuộc chủ đề |
| `categories` | không | Mảng chuyên mục, giới hạn thêm: chỉ lấy bài thuộc các chuyên mục này |
| `desc` | không | Mô tả ngắn dưới tên chủ đề trong dropdown, thẻ chủ đề, meta description |
| `href` | không | Link thay thế. Có `href` thì **không** sinh trang chủ đề; menu trỏ thẳng tới `href`. Hiện chưa chủ đề nào dùng. |

Không có `tags` lẫn `categories` thì chủ đề luôn rỗng. Chủ đề rỗng vẫn có trang, hiện "Nội dung đang được
biên soạn", meta `noindex, follow`, không có trong sitemap, và đếm là "Sắp có" trên menu.

Lưu ý: chủ đề trong mục này có thể gom bài của chuyên mục khác. Ví dụ `kien-thuc/computer-vision` lấy mọi
bài có tag `Computer Vision`, kể cả bài thuộc `hoc`. Dùng `categories` nếu muốn tách.

### `popularTopics`

Mảng `ref` chủ đề. Dùng cho chip "Chủ đề phổ biến" trong hộp tìm kiếm và lưới chủ đề trên trang chủ. Icon
trên trang chủ lấy từ bảng `TOPIC_ICON` trong `build.py` (chủ đề không có trong bảng dùng icon `sparkles`).

## `src/learning-paths.json`

```json
{ "paths": [ {lộ trình}, … ] }
```

Hướng dẫn thêm và sửa lộ trình ở [05. Learning Paths](05-lo-trinh-hoc.md). Bảng dưới là tham chiếu trường.

### Lộ trình (`paths[]`)

| Trường | Bắt buộc | Ý nghĩa |
|---|---|---|
| `slug` | có | Trang `lo-trinh/<slug>.html`; khóa `localStorage` `hf-path-<slug>`, `hf-lessons-<slug>` |
| `flagship` | không | `true` cho đúng **một** lộ trình (hiện là `vision-engineer`): huy hiệu ⭐, hero trang chủ, gợi ý trong hộp tìm kiếm. Trang chủ cần có lộ trình flagship. |
| `label` | có | Tên đầy đủ, ví dụ `Trở thành Vision Engineer` |
| `short` | có | Tên ngắn trong breadcrumb, thanh khóa học, ví dụ `Vision Engineer` |
| `tagline` | có | Một dòng giới thiệu |
| `description` | có | Đoạn mô tả, meta description |
| `duration`, `pace` | có (nếu có `steps`) | `~13 tháng`, `8–10 giờ/tuần` |
| `preview` | có (nếu có `steps`) | 3–4 chặng tiêu biểu hiện thành chuỗi trên thẻ lộ trình |
| `entryPoints[]` | có (nếu có `steps`) | Khối "Bạn đang ở đâu?": `label`, `detail`, `step` (slug chặng để bắt đầu) |
| `phases[]` | có (nếu có `steps`) | Giai đoạn theo thứ tự: `slug`, `label` |
| `goal` | có (nếu có `steps`) | Đích đến: `title`, `summary`, `can[]` (làm được gì), `roles[]`, `rolesLabel` (mặc định `Vị trí có thể ứng tuyển`) |
| `practiceNote` | không | Câu nhắc dưới khối bài tập của mọi bài học trong lộ trình |
| `steps[]` | không | Không có `steps`: lộ trình hiện "Sắp ra mắt", link tới `lo-trinh/#<slug>`, không sinh trang riêng |

### Chặng (`steps[]`)

| Trường | Ý nghĩa |
|---|---|
| `slug` | Trang `lo-trinh/<lộ-trình>/<slug>.html`, anchor `#step-<slug>` trên trang lộ trình |
| `phase` | `slug` của một giai đoạn trong `phases` |
| `title` | Tên chặng |
| `weeks` | Số tuần ước tính; tổng tuần của lộ trình và giai đoạn được cộng từ đây |
| `learn[]` | Gạch đầu dòng "Bạn sẽ học" |
| `outcome` | "Học xong bạn có thể…" (một câu) |
| `topics[]` | `ref` chủ đề trong `nav.json`. Phải tồn tại. Tạo chip trên trang lộ trình, banner "Học theo thứ tự" và widget "Có trong lộ trình" trên trang chủ đề. |
| `before` | Đoạn "Trước khi bắt đầu" trên trang chặng |
| `lessons[]` | Bài học theo đúng thứ tự (bảng dưới) |
| `extras[]` | Slug bài "Đọc thêm" (không bắt buộc học). **Phải tồn tại** trong `posts.json`. |

### Bài học (`lessons[]`)

| Trường | Ý nghĩa |
|---|---|
| `slug` | Slug bài viết. Có trong `posts.json` → trang bài học đầy đủ. Chưa có → dòng "Đang biên soạn". Một slug chỉ được là bài học của **một** chặng trong toàn bộ các lộ trình. |
| `kind` | `lesson` (Bài học), `lab` (Thực hành) hoặc `project` (Dự án) |
| `min` | Số phút học ước tính; tổng `min` của chặng ra số giờ |
| `title` | Tên bài trong giáo trình (có thể khác `title` của bài viết) |
| `goals[]` | "Học xong bài này, bạn sẽ…" |
| `practice[]` | Không bắt buộc. Danh sách bài tập cuối bài học |

## `src/icons.json`

```json
{ "_doc": "…", "icons": { "book-open": "<path d=\"…\" /> …", … } }
```

Mỗi giá trị là phần **bên trong** thẻ `<svg viewBox="0 0 24 24">` của một icon [Lucide](https://lucide.dev)
(giấy phép ISC). Dùng trong `build.py` bằng `icon("book-open")` hoặc `icon("check", "lớp-css")`. Có 29 icon
(05/11/2026). Thêm icon: lấy SVG từ gói npm `lucide-static` hoặc trang lucide.dev, chép phần giữa
`<svg …>` và `</svg>`.

Một vài icon nhỏ dùng ở khung trang (search, moon, menu, close…) nằm trong từ điển `ICON` ngay trong
`build.py`, không thuộc `icons.json`.

## `src/editorial-plan.json`

Kế hoạch cho quy trình đăng bài tự động ([auto-publish.md](auto-publish.md)). `build.py` **không** đọc file này.

| Trường | Ý nghĩa |
|---|---|
| `timezone`, `publish_time`, `posts_per_day` | `Asia/Ho_Chi_Minh`, `05:00`, `10` |
| `topics` | `ref` → `{category, menu, tags}`: chuyên mục cho bài mới, đường dẫn menu (để báo cáo), tag của chủ đề. 45 chủ đề (không gồm English, Chinese). |
| `days[]` | `day` (1–20), `date`, `topics[]` (10 ref), `status` (`pending`/`published`), `posts[]` (slug đã đăng) |

Ngày 05/11/2026: kế hoạch chạy từ 10/10 đến 29/10/2026, mới ngày 1 có `status: published`, 19 ngày còn
`pending` đã qua hạn. Muốn chạy tiếp cần đặt lại `date` cho các ngày còn lại.
