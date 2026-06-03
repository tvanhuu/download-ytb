# =============================================================================
#  CONFIG — Chỉnh sửa tất cả cài đặt tại đây
# =============================================================================


# ─────────────────────────────────────────────
#  PLAYLIST
# ─────────────────────────────────────────────

# URL playlist YouTube muốn tải (dùng khi không truyền argument từ CLI)
# PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLYaaU301HUe06Zlf3qv9q2dnVulj35gOb" # PHÀM NHÂN TU TIÊN 2
PLAYLIST_URL = "https://www.youtube.com/playlist?list=PL6j_JhY0whHHRyxqzy-DW1w3E7V4r92rC"


# ─────────────────────────────────────────────
#  THƯ MỤC LƯU FILE
# ─────────────────────────────────────────────

# Thư mục gốc chứa tất cả file tải về
OUTPUT_DIR = "./downloads"

# Thư mục con cho từng loại (tự động tạo nếu chưa có)
VIDEO_SUBDIR = "videos"   # → ./downloads/videos/
AUDIO_SUBDIR = "audio"    # → ./downloads/audio/


# ─────────────────────────────────────────────
#  CHẤT LƯỢNG VIDEO
# ─────────────────────────────────────────────

# Độ phân giải tối đa khi tải video
# Các lựa chọn: "360p" | "480p" | "720p" | "1080p" | "1440p" | "2160p"
RESOLUTION = "720p"

# Định dạng container đầu ra
# Các lựa chọn: "mp4" | "mkv" | "webm"
VIDEO_FORMAT = "mp4"


# ─────────────────────────────────────────────
#  CHẤT LƯỢNG AUDIO
# ─────────────────────────────────────────────

# Bitrate MP3 (kbps)
# Các lựa chọn: "128" | "192" | "256" | "320"
AUDIO_QUALITY = "192"

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

# Số lần retry khi gặp lỗi mạng
RETRIES = 3
FRAGMENT_RETRIES = 3

# Thời gian nghỉ giữa mỗi request (giây) — giúp tránh bị block
SLEEP_INTERVAL = 1       # Giữa các video
SLEEP_INTERVAL_MIN = 1   # Nghỉ tối thiểu (giây)
SLEEP_INTERVAL_MAX = 3   # Nghỉ tối đa (giây)


# ─────────────────────────────────────────────
#  FILE ARCHIVE (RESUME)
# ─────────────────────────────────────────────

# File lưu danh sách video đã tải — dùng để bỏ qua khi chạy lại
# Đặt None để tắt tính năng này
ARCHIVE_FILE = "./downloads/archive.txt"


# ─────────────────────────────────────────────
#  LOG
# ─────────────────────────────────────────────

# File lưu log lỗi
LOG_FILE = "./downloads/error.log"

# Hiển thị log chi tiết ra terminal (True/False)
VERBOSE = False
