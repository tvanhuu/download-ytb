# =============================================================================
#  CONFIG — Chỉnh sửa tất cả cài đặt tại đây
# =============================================================================


# ─────────────────────────────────────────────
#  DANH SÁCH PLAYLIST
# ─────────────────────────────────────────────

# Mảng playlist YouTube — mỗi item là 1 playlist riêng biệt
# Mỗi item gồm:
#   - url    : URL playlist YouTube (bắt buộc)
#   - subdir : Tên thư mục con lưu file (bắt buộc)
#              → file sẽ nằm trong: downloads/audio/<subdir>/ hoặc downloads/videos/<subdir>/
#   - skip   : Danh sách video bỏ qua cho playlist này (tuỳ chọn, mặc định [])
#              Hỗ trợ số thứ tự (int) hoặc video ID (str)
#
# Ví dụ:
#   PLAYLISTS = [
#       {
#           "url": "https://www.youtube.com/playlist?list=PLxxx",
#           "subdir": "ten-truyen",
#           "skip": [3, "dQw4w9WgXcQ"],
#       },
#       {
#           "url": "https://www.youtube.com/playlist?list=PLyyy",
#           "subdir": "ten-truyen-2",
#       },
#   ]

PLAYLISTS = [
    # {
    #     "url": "https://www.youtube.com/playlist?list=PLYaaU301HUe2LkN6ZxJLZzaxgvEdb80Np",
    #     "subdir": "ma-thien-ky",
    #     "skip": [
    #         "Z6qH-rhdSIw", "-xIZjbuZAN8", "kWE1O65dMY0", "24fyV_wicYo",
    #         "ARIyZkA5FF0", "AefATzHCR7k", "gSKZDU12S6s", "dj9IgI8W1ZY",
    #         "opmjdWcClCQ", "gD6OCieWczY", "tk4s_edISxI", "Maz3GxIqCyU",
    #         "DFtCsqbx6sY", "O_VFLhStEGM", "zOtvm9g9zx8", "48ghpKlRXC4",
    #         "5WP-n0E06jw", "nw_7wsxlhEQ", "3X8CshJrAQ4", "dKWj74rpnBE",
    #         "2c-fatddwFw", "s3lHq7QKlbY", "CLmwYTtrprQ", "_2Kdg8dir0Q",
    #     ],
    # },
    {
        "url": "https://www.youtube.com/playlist?list=PLO8qhgcGpJ0vIru3cVcSFZ7YSRLo7jTPe",
        "subdir": "thai-hu-chi-ton",
    },
    {
        "url": "https://www.youtube.com/playlist?list=PLO8qhgcGpJ0s7twqdqKzwXKwLDCdk3Ryv",
        "subdir": "nhat-niem-than-ma",
    },
    {
        "url": "https://www.youtube.com/playlist?list=PLO8qhgcGpJ0tlnEDewjcPhqNWLjxiy1m5",
        "subdir": "vinh-hang-chi-mon",
    },
    {
        "url": "https://www.youtube.com/playlist?list=PLYaaU301HUe2lwl0pMsxdMvG-d8xlTkCK",
        "subdir": "luong-tam",
    },
    {
        "url": "https://www.youtube.com/playlist?list=PLlX4DdjnK14M-xZj6j8B22zkbD6fBvNFc",
        "subdir": "quan-am-chi-mgoai",
    },
]

# Fallback — dùng khi PLAYLISTS trống (backward compatible)
PLAYLIST_URL = ""

# Global skip — áp dụng cho TẤT CẢ playlist (merge với skip riêng từng playlist)
# Hỗ trợ số thứ tự (int) hoặc video ID (str)
SKIP_VIDEOS: list[int | str] = []


# ─────────────────────────────────────────────
#  THƯ MỤC LƯU FILE
# ─────────────────────────────────────────────

# Thư mục gốc chứa tất cả file tải về
# OUTPUT_DIR = "./downloads/"
OUTPUT_DIR = r"E:\audio-stream-data\audios\mp3"

# Thư mục con cho từng loại (tự động tạo nếu chưa có)
# Thư mục cụ thể cho từng truyện được khai báo trong PLAYLISTS[].subdir
# Ví dụ: downloads/audio/ma-thien-ky/, downloads/videos/tien-nghich/
VIDEO_SUBDIR = "videos"   # → ./downloads/videos/<subdir>/
AUDIO_SUBDIR = "audio"    # → ./downloads/audio/<subdir>/



# ─────────────────────────────────────────────
#  CHẤT LƯỢNG VIDEO
# ─────────────────────────────────────────────

# Độ phân giải tối đa khi tải video
# Các lựa chọn: "360p" | "480p" | "720p" | "1080p" | "1440p" | "2160p" | "max"
# "max" = tải chất lượng cao nhất có sẵn (không giới hạn)
RESOLUTION = "max"

# Định dạng container đầu ra
# Các lựa chọn: "mp4" | "mkv" | "webm"
VIDEO_FORMAT = "mp4"

# Chế độ phụ đề (subtitle)
# Các lựa chọn:
#   "none"     — chỉ tải video, không tải phụ đề
#   "embed"    — tải video + nhúng phụ đề vào file video
#   "separate" — tải video + phụ đề riêng (2 file tách biệt)
#   "only"     — chỉ tải phụ đề (không tải video)
SUBTITLE_MODE = "none"

# Ngôn ngữ phụ đề ưu tiên (ISO 639-1 code)
# Ví dụ: "vi" (Việt), "en" (Anh), "zh-Hans" (Trung giản thể), "ja" (Nhật)
# Dùng "all" để tải tất cả ngôn ngữ có sẵn
SUBTITLE_LANGS = "vi"
# ─────────────────────────────────────────────
#  CHẤT LƯỢNG AUDIO
# ─────────────────────────────────────────────

# Bitrate MP3 (kbps)
# Các lựa chọn: "128" | "192" | "256" | "320"
AUDIO_QUALITY = "128"

# Định dạng audio đầu ra
# Các lựa chọn: "mp3" | "m4a" | "wav" | "flac"
AUDIO_FORMAT = "mp3"


# ─────────────────────────────────────────────
#  MẠNG & TỐC ĐỘ
# ─────────────────────────────────────────────

# Giới hạn tốc độ tải (bytes/s). None = không giới hạn
# Ví dụ: 1_000_000 = 1 MB/s | 2_000_000 = 2 MB/s
RATE_LIMIT = None

# Kích thước chunk HTTP (bytes) — tăng nếu mạng tốt
HTTP_CHUNK_SIZE = 10 * 1024 * 1024   # 10 MB

# Số lần retry khi gặp lỗi mạng (cho từng fragment/request bên trong yt-dlp)
RETRIES = 3
FRAGMENT_RETRIES = 3

# Số vòng retry cho video thất bại (sau khi chạy xong toàn bộ playlist)
# Ví dụ: 2 = retry tối đa 2 lần cho mỗi video bị lỗi
MAX_DOWNLOAD_RETRIES = 2

# Thời gian nghỉ giữa mỗi request (giây) — giúp tránh bị block
SLEEP_INTERVAL = 1       # Giữa các video
SLEEP_INTERVAL_MIN = 1   # Nghỉ tối thiểu (giây)
SLEEP_INTERVAL_MAX = 3   # Nghỉ tối đa (giây)


# ─────────────────────────────────────────────
#  FILE ARCHIVE (RESUME)
# ─────────────────────────────────────────────

# File lưu danh sách video đã tải — dùng để bỏ qua khi chạy lại
# Đặt None để tắt tính năng này
ARCHIVE_FILE = "./archive.txt"


# ─────────────────────────────────────────────
#  LOG
# ─────────────────────────────────────────────

# File lưu log lỗi
LOG_FILE = "./error.log"

# Hiển thị log chi tiết ra terminal (True/False)
VERBOSE = False
