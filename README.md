# 📥 YouTube Playlist Downloader

Script Python tự động tải toàn bộ video hoặc audio từ một playlist YouTube, với progress bar, resume hỗ trợ, và log lỗi.

---

## ✨ Tính năng

- 📋 **Liệt kê playlist** — hiển thị toàn bộ danh sách video trước khi tải
- 📹 **Tải video** — MP4, chọn chất lượng (360p → 1080p → max)
- 🎵 **Tải audio** — MP3, chọn bitrate (128 → 320 kbps)
- 💬 **Phụ đề** — nhúng vào video, hoặc tải riêng file phụ đề
- ⏭️ **Resume** — bỏ qua video đã tải nhờ `archive.txt`
- 🚫 **Skip videos** — bỏ qua video cụ thể theo số thứ tự hoặc video ID
- 📊 **Progress bar** — thanh tiến trình riêng cho từng video (tqdm)
- 📝 **Log lỗi** — ghi lỗi ra file để review sau
- 🔧 **Preflight check** — kiểm tra `ffmpeg` trước khi chạy
- 🛡️ **Sanitize tên file** — xử lý ký tự đặc biệt an toàn trên mọi OS

---

## 📁 Cấu trúc project

```
download_yt/
├── main.py           # Script chính — chạy file này
├── download_yt.py    # Hàm download đơn lẻ (video/audio)
├── config.py         # ⚙️  Toàn bộ cài đặt tập trung tại đây
├── requirements.txt  # Dependencies Python
├── Makefile          # Shortcut lệnh
├── setup.sh          # Script cài đặt môi trường
├── run.sh            # Script chạy chương trình
└── downloads/        # Thư mục lưu file (tự tạo)
    ├── videos/       # Video MP4
    ├── audio/        # Audio MP3
    └── archive.txt   # Danh sách video đã tải (resume)
```

---

## 🚀 Cài đặt

### Yêu cầu

- Python 3.10+
- `ffmpeg` (bắt buộc khi tải audio hoặc merge video)

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### Cài dependencies

```bash
# Clone / tải project về
cd download_yt

# Cài Python packages
pip install -r requirements.txt

# Hoặc dùng Makefile
make install
```

---

## ⚙️ Cấu hình

Chỉnh sửa file **`config.py`** — không cần sửa code ở chỗ nào khác:

```python
# URL playlist mặc định
PLAYLIST_URL = "https://www.youtube.com/playlist?list=..."

# Thư mục lưu file
OUTPUT_DIR   = "./downloads"

# Chất lượng video: "360p" | "480p" | "720p" | "1080p" | "max"
# "max" = tải chất lượng cao nhất có sẵn
RESOLUTION   = "720p"

# Phụ đề: "none" | "embed" | "only"
SUBTITLE_MODE = "embed"
SUBTITLE_LANGS = "vi,en"    # ngôn ngữ ưu tiên

# Bitrate audio: "128" | "192" | "256" | "320"
AUDIO_QUALITY = "192"

# Giới hạn tốc độ tải (None = không giới hạn)
RATE_LIMIT = None

# Bỏ qua video cụ thể — theo số thứ tự (int) hoặc video ID (str)
SKIP_VIDEOS = [3, 7, "dQw4w9WgXcQ"]

# File lưu danh sách đã tải (resume)
ARCHIVE_FILE = "./downloads/archive.txt"

# File ghi log lỗi
LOG_FILE = "./downloads/error.log"
```

---

## 🎯 Cách dùng

### Cách 1: Truyền URL qua argument (khuyên dùng)

```bash
python main.py "https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxxx"
```

### Cách 2: Sửa `PLAYLIST_URL` trong `config.py` rồi chạy

```bash
python main.py
```

### Cách 3: Dùng Makefile

```bash
make run
```

---

## 📊 Luồng hoạt động

```
python main.py [URL]
      │
      ▼
① Lấy thông tin playlist (không tải)
      │
      ▼
② Hiển thị bảng danh sách video
  ┌──────────────────────────────────────────────────────────────────────┐
  │  📋  Python Tutorial for Beginners                                   │
  │  👤  Tech Channel          📦  47 video                             │
  │  🚫  Bỏ qua (config): 2 video                                       │
  │  ────────────────────────────────────────────────────────────────    │
  │     #  Tiêu đề                                          Thời lượng  │
  │     1  Python Installation Guide                          0:10:23   │
  │     2  Variables and Data Types                           0:15:47   │
  │     3  Old Intro Video (deprecated)                       0:02:11  ⛔│
  │   ...                                                               │
  └──────────────────────────────────────────────────────────────────────┘
      │
      ▼
③ Chọn định dạng
  1. 📹 Video (MP4)
  2. 🎵 Audio (MP3)
  0. ❌ Thoát
      │
      ▼
④ Kiểm tra môi trường (ffmpeg)
      │
      ▼
⑤ Tải từng video với progress bar
  [  1/ 47] Python Installation Guide   |████████░░| 54M/100M [00:12<00:10] 5MB/s
  [  2/ 47] Variables and Data Types    |██████████| 87M/87M  [00:18<00:00] ✔ xong
  ⏭  [3/47] Bỏ qua (đã tải): Control Flow
      │
      ▼
⑥ Summary
  ✅ Tải mới  : 44
  ⏭  Bỏ qua  : 3   (đã có trong archive)
  ❌ Lỗi     : 0
  📁 Lưu tại : ./downloads/videos
```

---

## 🚫 Skip Videos — bỏ qua video cụ thể

Khi playlist có một vài video bạn không muốn tải (intro, outro, video trùng...), thêm chúng vào `SKIP_VIDEOS` trong `config.py`:

```python
# Bỏ qua theo số thứ tự trong playlist
SKIP_VIDEOS = [1, 5, 10]

# Bỏ qua theo YouTube video ID
SKIP_VIDEOS = ["dQw4w9WgXcQ", "abc123xyz"]

# Kết hợp cả hai
SKIP_VIDEOS = [1, "dQw4w9WgXcQ", 10]

# Không bỏ qua video nào (mặc định)
SKIP_VIDEOS = []
```

Video bị skip sẽ hiển thị với ⛔ trong bảng danh sách và **không được tải**:

```
     #  Tiêu đề                                          Thời lượng
     1  Python Installation Guide                          0:10:23
     2  Old Intro Video                                    0:02:11  ⛔
     3  Variables and Data Types                           0:15:47
```

> 💡 **Tip**: Chạy script 1 lần trước để xem bảng danh sách, ghi lại số thứ tự của video muốn bỏ qua, rồi thêm vào `SKIP_VIDEOS`.

---

## 💬 Phụ đề (Subtitle)

Cấu hình `SUBTITLE_MODE` trong `config.py` để chọn cách xử lý phụ đề:

| Mode | Mô tả |
|------|--------|
| `"none"` | Chỉ tải video, không tải phụ đề **(mặc định)** |
| `"embed"` | Tải video + nhúng phụ đề vào file MP4 |
| `"separate"` | Tải video + phụ đề riêng (2 file tách biệt: `.mp4` + `.srt`) |
| `"only"` | Chỉ tải file phụ đề (SRT), không tải video |

```python
# Tải video + nhúng phụ đề tiếng Việt và Anh
SUBTITLE_MODE  = "embed"
SUBTITLE_LANGS = "vi,en"

# Tải video + phụ đề file riêng (không nhúng)
SUBTITLE_MODE  = "separate"
SUBTITLE_LANGS = "vi,en"

# Chỉ tải phụ đề (không tải video)
SUBTITLE_MODE  = "only"
SUBTITLE_LANGS = "vi,en,zh-Hans"

# Tải tất cả ngôn ngữ phụ đề có sẵn
SUBTITLE_LANGS = "all"
```

> ⚠️ **Lưu ý**: Chế độ phụ đề chỉ áp dụng khi chọn tải **Video (MP4)**, không áp dụng khi tải Audio.
> Cần `ffmpeg` để nhúng phụ đề vào video (mode `"embed"`).

---

## 🔁 Resume — tải tiếp khi bị ngắt

Script tự động ghi ID của video đã tải vào `archive.txt`. Lần chạy tiếp theo sẽ **bỏ qua** các video đã có:

```bash
# Chạy lại — chỉ tải video chưa có
python main.py "https://youtube.com/playlist?list=..."
# ⏭  [1/47] Bỏ qua (đã tải): Video 1
# ⏭  [2/47] Bỏ qua (đã tải): Video 2
# ⬇  [3/47] Đang tải: Video 3 ...
```

Để **tải lại từ đầu**, xóa file archive:

```bash
rm ./downloads/archive.txt
```

---

## 📝 Log lỗi

Khi có video tải thất bại, lỗi được ghi vào `downloads/error.log`:

```
2026-06-03 08:35:12 [ERROR] [3/47] Video name — HTTP Error 403: Forbidden
2026-06-03 08:36:01 [WARNING] Some format not available, falling back
```

---

## 🔧 Makefile commands

```bash
make help     # Xem danh sách lệnh
make install  # Cài dependencies
make run      # Chạy chương trình
make setup    # Thiết lập môi trường (venv)
make clean    # Xóa venv
```

---

## 📦 Dependencies

| Package | Phiên bản | Mục đích |
|---------|-----------|----------|
| `yt-dlp` | ≥ 2024.9.12 | Download engine |
| `tqdm` | ≥ 4.0 | Progress bar |
| `ffmpeg` | bất kỳ | Merge video+audio, convert MP3 |

---

## ❓ Lấy Playlist ID ở đâu?

Mở playlist trên YouTube, copy URL từ trình duyệt:

```
https://www.youtube.com/playlist?list=PLRqwX-V7Uu6ZiZxtBx7kQPV4OamFXlreZ
                                       ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
                                       Playlist ID
```

Paste cả URL vào lệnh hoặc vào `PLAYLIST_URL` trong `config.py`.

---

## ⚠️ Lưu ý

- Script chỉ tải được video/playlist **công khai**. Playlist private cần cookie đăng nhập.
- Tôn trọng bản quyền — chỉ tải nội dung bạn có quyền sử dụng.
- Không dùng để tải hàng loạt với tốc độ cao, có thể bị YouTube chặn IP.
