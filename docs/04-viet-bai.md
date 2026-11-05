# 04. Hướng dẫn viết bài

Tài liệu cho người viết và biên tập nội dung. Phần kỹ thuật tối thiểu: sửa hai file văn bản, chạy ba lệnh.

## Quy trình một bài mới

1. **Chọn đề tài** chưa có trên site. Tìm nhanh: `grep -i "từ khóa" src/posts.json`, hoặc gõ vào ô tìm
   kiếm của site đang chạy.
2. **Khai báo bài** bằng một dòng mới trong mảng `posts` của `src/posts.json`
   (bảng trường ở [03. Dữ liệu nguồn](03-du-lieu-nguon.md#bài-viết-posts)):

   ```json
   {"slug": "hieu-chuan-camera-ban-co-opencv", "category": "hoc", "title": "Hiệu chuẩn camera bằng bàn cờ với OpenCV", "excerpt": "…", "date": "2026-11-05", "tags": ["Calibration", "OpenCV", "Python"], "thumb": {"glyph": "K, D", "colors": ["#0ea5e9", "#082f49"]}}
   ```

3. **Viết thân bài** trong `src/posts/<slug>.html`.
4. **Build và kiểm tra:**

   ```bash
   python tools/make_thumbs.py
   python tools/build.py
   python tools/check_site.py
   ```

5. **Xem thử** bằng `python -m http.server 8000`, mở `http://localhost:8000/<category>/<slug>.html`.
6. Commit nguồn cùng file sinh ra.

## Thông tin bài

### Slug

Chữ thường, không dấu, nối bằng `-`, mô tả nội dung: `opencv-co-ban-anh-video-camera`,
`hsk3-thanh-dieu`. Bài thuộc một chuỗi dùng chung tiền tố: `python-3-…`, `pydev-…`, `3d-vision-2-…`.
Slug là URL vĩnh viễn: **không đổi sau khi đăng**.

### Tiêu đề và đoạn dẫn

- `title` ≤ 70 ký tự, nói rõ người đọc nhận được gì. Tốt: `4 thanh điệu và thanh nhẹ tiếng Trung: so sánh với
  dấu tiếng Việt`. Tránh: `Tìm hiểu về thanh điệu`.
- `excerpt` 120–170 ký tự, chứa thông tin cụ thể (con số, tên công cụ, kết quả). Đoạn này là meta description
  trên Google và đoạn dẫn ngay dưới `<h1>`, nên **đừng lặp lại nó ở đoạn đầu thân bài**.

### Chuyên mục và tag

`category` quyết định bài nằm ở thư mục nào. `tags` quyết định bài hiện ở **trang chủ đề** nào. Muốn bài
hiện trong `Học AI & Lập trình › Object Detection`, bài phải có tag `Object Detection` hoặc `YOLO` (tag của
chủ đề đó trong `nav.json`).

Tra tag của mọi chủ đề:

```bash
python -X utf8 -c "import json;[print(s['slug']+'/'+i['slug'], i.get('tags')) for s in json.load(open('src/nav.json',encoding='utf-8'))['sections'] for g in s.get('groups',[]) for i in g['items']]"
```

Thường dùng 2–4 tag: một tag chủ đề chính và 1–3 tag có sẵn liên quan. Tạo tag mới chỉ khi thật cần, vì mỗi
tag xuất hiện trong mây thẻ ở sidebar của mọi trang.

## Thân bài

`src/posts/<slug>.html` chỉ chứa **phần thân**: không `<html>`, `<head>`, `<body>`, không `<h1>` (tiêu đề do
`build.py` tạo), không `style="…"`, không `<script>`. Mọi thứ nằm trong khung `<div class="prose">`.

### Thẻ dùng được

| Thẻ | Dùng cho |
|---|---|
| `<h2>`, `<h3>` | Mục và mục con. Không dùng `<h4>` trở xuống trừ khi thật cần. |
| `<p>`, `<ul>`, `<ol>`, `<li>` | Đoạn văn, danh sách |
| `<strong>`, `<em>`, `<code>`, `<kbd>`, `<sub>`, `<sup>`, `<br>` | Nhấn mạnh, tên hàm/biến, phím tắt, chỉ số |
| `<a href="…">` | Liên kết |
| `<table>` (có thể kèm `<thead>`, `<tbody>`, `<caption>`) | Bảng |
| `<pre><code class="language-…">` | Khối code |
| `<blockquote>` | Trích dẫn |
| `<details><summary>` | Nội dung ẩn: đáp án, lời giải |
| `<figure class="diagram">` + `<svg class="dg">` + `<figcaption>` | Sơ đồ vẽ bằng SVG |

### Tiêu đề và mục lục

- `build.py` tự gắn `id` cho mọi `<h2>` và `<h3>` từ nội dung tiêu đề (bỏ dấu, chữ thường, nối `-`):
  `<h2>Cài đặt OpenCV</h2>` thành `<h2 id="cai-dat-opencv">`.
- Bài có **từ 3 `<h2>` trở lên** tự có hộp "Nội dung bài viết" (mục lục). Nếu tiêu đề đã tự đánh số
  (`<h2>1. Cài đặt</h2>`) thì mục lục không đánh số chồng.
- Viết thẻ tiêu đề **trên một dòng** và **không kèm thuộc tính** (`<h2>…</h2>`), nếu không sẽ không được gắn
  id và không vào mục lục.
- Giữ tiêu đề không trùng nhau trong một bài: hai tiêu đề giống hệt sẽ sinh hai id giống nhau.
- Link tới một mục trong bài: `<a href="#cai-dat-opencv">`. `check_site.py` kiểm tra anchor có tồn tại.

### Liên kết

| Tới | Viết |
|---|---|
| Bài cùng chuyên mục | `<a href="opencv-co-ban-anh-video-camera.html">` |
| Bài khác chuyên mục | `<a href="../kien-thuc/vs-code-cho-python-va-ai.html">` |
| Trang chủ đề | `<a href="../hoc/opencv.html">` |
| Lộ trình, chặng | `<a href="../lo-trinh/vision-engineer.html">`, `<a href="../lo-trinh/vision-engineer/python.html">` |
| Trang ngoài | `<a href="https://…" target="_blank" rel="noopener">` |

Mọi link nội bộ là **đường dẫn tương đối** tính từ thư mục chuyên mục của bài. `check_site.py` báo mọi link
nội bộ hỏng.

### Các khối trình bày có sẵn

Các lớp CSS này đã có trong `assets/css/style.css`. Không tự thêm lớp mới trong bài nếu chưa thêm CSS.

**Mẹo và cảnh báo** (`tip` xanh, `warn` vàng). `<strong>` đầu tiên thành dòng tiêu đề:

```html
<div class="tip"><strong>Dùng lại công cụ 2D trên bản đồ chiều cao</strong>Nội dung mẹo…</div>
<div class="warn"><strong>Độ chụm không phải độ đúng</strong>Nội dung cảnh báo…</div>
```

**Bài tập có đáp án ẩn** (`ex` + `details`):

```html
<h2>Bài tập</h2>
<div class="ex">
<h3>Bài 1. Kích thước trường nhìn</h3>
<p>Đề bài…</p>
<details><summary>Xem đáp án</summary>
<pre><code class="language-python">…</code></pre>
<pre><code class="language-text">Kết quả in ra…</code></pre>
<p>Giải thích…</p>
</details>
</div>
```

**Hội thoại và phiên âm** (bài ngoại ngữ): `dlg` là khối hội thoại có viền trái, `py` là dòng pinyin màu nhạt.

```html
<div class="dlg">
<p><strong>A:</strong> 我饿了。<br><span class="py">Wǒ è le.</span><br><em>Mình đói rồi.</em></p>
</div>
```

**Ghi chú nguồn** cuối bài (bắt buộc khi bài dùng dữ kiện bên ngoài):

```html
<p class="note">Nguồn tham khảo: <a href="https://…" rel="noopener" target="_blank">Tên tài liệu</a>, <a href="https://…" rel="noopener" target="_blank">…</a>.</p>
```

**Bảng.** Viết `<table>` bình thường. `main.js` tự bọc mỗi bảng trong `<div class="table-wrap">` để cuộn ngang
trên điện thoại, nên **không cần tự bọc** (tự bọc sẽ thành hai lớp khung). Ô canh giữa: `<td class="c">`.

**Ma trận số** (bài Deep Learning): `<table class="mat">`, ô tô màu `td.hl` (xanh) và `td.hl2` (cam), đặt nhiều
ma trận cạnh nhau trong `<div class="mats">` với dấu phép tính `<span class="op">×</span>`.

**Sơ đồ SVG.** Vẽ trực tiếp bằng SVG để tự đổi màu theo chế độ sáng/tối:

```html
<figure class="diagram">
<svg class="dg" viewBox="0 0 640 220" role="img" aria-label="Mô tả sơ đồ cho trình đọc màn hình">
  <rect class="bx" x="20" y="80" width="120" height="50" rx="8"/>
  <text x="80" y="110" text-anchor="middle">Camera</text>
  <path class="ln-a" d="M140 105H240"/>
</svg>
<figcaption>Chú thích sơ đồ.</figcaption>
</figure>
```

| Lớp | Tác dụng |
|---|---|
| `bx`, `bx-c`, `bx-a` | Hộp nền xám, viền xám / xanh / cam |
| `ln`, `ln-a` | Đường xám / cam |
| `s-c`, `s-a` | Viền xanh / cam |
| `f-c-soft`, `f-a-soft`, `f-ink` | Tô nhạt xanh / cam / màu chữ |
| `t-c`, `t-a`, `f-c` | Chữ xanh / cam |
| `sm` | Chữ nhỏ màu nhạt |

Dùng lớp thay vì màu cố định (`fill="#000"`) để sơ đồ đọc được ở cả hai chế độ.

**Ảnh trong bài.** Hiện chưa bài nào chèn ảnh trong thân bài. Nếu cần, đặt ảnh trong `assets/images/`
(ví dụ `assets/images/posts/<slug>-1.webp`), chèn bằng `<img src="../assets/images/posts/<slug>-1.webp"
alt="mô tả" width="…" height="…" loading="lazy">` và kiểm tra lại trên điện thoại.

### Code mẫu

```html
<pre><code class="language-python">import cv2

anh = cv2.imread("pcb.png")
if anh is None:
    raise FileNotFoundError("Không đọc được pcb.png")
print(anh.shape)</code></pre>
```

Quy tắc:

- Viết `<pre><code` **liền nhau**, nội dung bắt đầu ngay sau `>`, kết thúc bằng `</code></pre>`.
- **Escape** trong code: `<` thành `&lt;`, `>` thành `&gt;`, `&` thành `&amp;`. Ví dụ `a &lt;= b`,
  `List&lt;int&gt;`, `cmd1 &amp;&amp; cmd2`. Thẻ duy nhất được phép trong code là `<span>`, `<b>`, `<i>`,
  `<em>`, `<strong>`.
- Lớp ngôn ngữ đang dùng: `language-python`, `language-text` (kết quả in ra màn hình, nền xanh đậm),
  `language-bash`, `language-csharp`, `language-markdown`, `language-dockerfile`, `language-yaml`,
  `language-xml`. Không có tô màu cú pháp; lớp chỉ đổi nền và giúp đọc nguồn.
- Đặt kết quả chạy ngay dưới code trong một khối `language-text` riêng.
- Code phải **chạy được**: đủ import, đúng API của phiên bản thư viện hiện hành, tên biến tiếng Việt không dấu
  (`anh`, `ket_qua`) hoặc tiếng Anh, chú thích tiếng Việt có dấu.
- Nút "Sao chép" được thêm tự động cho mọi khối `<pre>`.

**Kiểm tra cú pháp Python tự động.** `check_site.py` chạy `ast.parse` trên mọi khối code trông giống Python
(có dòng bắt đầu bằng `import `, `from … import`, `def ` hoặc `for … in …:`), trừ khối có dòng bắt đầu bằng
`using `, `public `, `var `, `$ `, `pip `, `git `, `docker `, `FROM `, `RUN `. Cần lưu ý:

- Trình thông dịch trên máy là Python 3.10. Đừng dùng cú pháp mới hơn trong code mẫu (generic PEP 695
  `def f[T](x: T)`, f-string lồng cùng loại nháy theo PEP 701, `type X = …`). Nêu cú pháp mới trong lời văn,
  còn code dùng dạng tương thích (`TypeVar`). Import API mới như `datetime.UTC` vẫn qua vì chỉ parse, không chạy.
- Khối **cố ý sai** để người học tự sửa: thêm chú thích chứa đúng chuỗi `(minh họa)`, ví dụ
  `# Code có lỗi (minh họa)`. `check_site.py` bỏ qua khối đó.
- `check_site.py` chỉ kiểm tra cú pháp. Muốn chắc code chạy đúng, chạy thử nó thật (nên dùng một môi trường
  Python mới trong thư mục tạm, không cài vào repo).

### Công thức toán

Thêm `"math": true` vào dòng của bài trong `posts.json`. Trang sẽ tải KaTeX tự host
(`assets/vendor/katex`, phiên bản 0.16.11).

- Cùng dòng: `\( \sigma(x) = \frac{1}{1 + e^{-x}} \)`
- Dòng riêng: `\[ L = -\sum_i y_i \log \hat{y}_i \]`

KaTeX chỉ xử lý trong `.prose` và bỏ qua `<pre>`/`<code>`. Lỗi cú pháp công thức không làm hỏng trang
(`throwOnError: false`), công thức lỗi hiện màu đỏ: luôn xem thử. Trong HTML vẫn phải escape `<` và `&`
(`\(a &lt; b\)`). Ngày 05/11/2026 có 22 bài dùng `math`.

### Hộp tải tài liệu

Viết `{{download:<key>}}` trên một dòng riêng, với `<key>` khai báo trong `downloads` của `posts.json`.
`build.py` thay bằng hộp có tiêu đề, mô tả và nút mở link. Key không tồn tại làm build dừng.

## Bài học trong lộ trình

Nếu slug của bài có trong `lessons` của một chặng ở `src/learning-paths.json`, trang bài tự có thêm: thanh
khóa học (lộ trình, chặng, "Bài N/M", loại bài, số phút), khối **"Học xong bài này, bạn sẽ"** từ `goals`,
khối **"Bài tập thực hành"** từ `practice`, nút "Đánh dấu đã học xong", nút bài trước/sau theo thứ tự giáo
trình và mục lục chặng ở sidebar. Vì các khối này sinh từ JSON, **đừng lặp lại mục tiêu và danh sách bài tập
của giáo trình trong thân bài**. Xem [05. Learning Paths](05-lo-trinh-hoc.md).

## Ảnh đại diện

Mỗi bài cần `assets/images/posts/<slug>.jpg` và `<slug>.webp`, tỉ lệ 16:9, chuẩn 1200×675.

**Ảnh tự vẽ** (mặc định): `python tools/make_thumbs.py` vẽ từ `thumb` trong `posts.json`:

- Nền tối pha từ màu thứ hai, quầng sáng màu thứ nhất, lưới mờ, vòng tròn đồng tâm bên phải.
- Chữ lớn `thumb.glyph` tô gradient trắng sang màu thứ nhất, font Be Vietnam Pro ExtraBold, tự thu nhỏ cho vừa.
  Glyph có chữ Hán dùng font hệ thống `wqy-zenhei.ttc` (Linux) hoặc `msyhbd.ttc` (Windows); ký hiệu đặc biệt
  (mũi tên, toán) dùng `DejaVuSans-Bold.ttf` hoặc `arialbd.ttf`.
- Nhãn chuyên mục góc trên trái, logo và `hocfree.vn` góc dưới trái.

Chọn `colors`: màu thứ nhất sáng, bão hòa (`#0ea5e9`), màu thứ hai cùng tông nhưng rất tối (`#082f49`). Các
bài trong một chuỗi nên dùng chung màu (ví dụ chuỗi HSK dùng `["#dc2626", "#450a0a"]`).

**Ảnh thật:** chép ảnh 16:9 vào `assets/images/posts/<slug>.jpg` rồi chạy `python tools/make_thumbs.py`. Script
thấy đã có `.jpg` nên không vẽ đè, chỉ tạo `.webp` từ ảnh đó. Đừng chạy `--all` sau khi đã có ảnh thật: lệnh đó
vẽ đè tất cả.

## Quy tắc nội dung

- **Tiếng Việt có dấu đầy đủ**, câu ngắn, dễ hiểu, có ví dụ thực tế (ưu tiên ngữ cảnh nhà máy, kỹ sư người
  Việt với các bài kỹ thuật). Thuật ngữ tiếng Anh phổ biến giữ nguyên, giải thích ở lần đầu xuất hiện.
- **Chính xác.** Kiểm tra phiên bản thư viện, tên hàm, tham số, số liệu bằng tài liệu chính thức. Không bịa số
  liệu, tên sản phẩm, trích dẫn hay nguồn. Không chắc thì không viết chi tiết đó.
- **Tin tức AI** (`tin-tuc-ai`): chỉ sự kiện có thật, khoảng 10 ngày gần nhất tính tới ngày đăng, đối chiếu
  ít nhất 2 nguồn khi có thể, ghi rõ nguồn.
- **Độ dài:** bài thường khoảng 700–1500 từ. Bài học trong giáo trình có thể dài hơn (trung vị toàn site
  khoảng 1.170 từ; nhiều bài học có bài tập vượt 3.000 từ). Thời gian đọc tự tính ở ~180 từ/phút.
- **Nguồn:** bài dùng dữ kiện bên ngoài kết bằng `<p class="note">Nguồn tham khảo: …</p>` với URL thật.
- Quy trình đăng tự động có thêm các ràng buộc riêng: xem [auto-publish.md](auto-publish.md).

## Danh sách kiểm tra trước khi commit

- [ ] Dòng trong `posts.json` đủ trường, `slug` mới, `category` đúng, `tags` có tag của chủ đề cần hiện.
- [ ] `title` ≤ 70 ký tự, `excerpt` 120–170 ký tự.
- [ ] Thân bài không có `<h1>`, style nội tuyến, script; tiêu đề `<h2>` không trùng nhau.
- [ ] Code đã escape `<`, `>`, `&`; code Python tương thích 3.10 và đã chạy thử.
- [ ] Mọi link nội bộ là tương đối và đúng chuyên mục; link ngoài có `target="_blank" rel="noopener"`.
- [ ] Có `Nguồn tham khảo` nếu dùng dữ kiện bên ngoài.
- [ ] `make_thumbs.py`, `build.py` chạy xong; `check_site.py` in `OK: không có lỗi`.
- [ ] Đã xem bài ở chế độ sáng, tối và màn hình hẹp; bài hiện đúng trên trang chủ đề.
