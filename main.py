import yt_dlp
import sys
import shutil
import logging
from pathlib import Path
from datetime import timedelta
from tqdm import tqdm

import config


# ═══════════════════════════════════════════════════════════════════════
#  [FIX 5] LOGGING — ghi lỗi ra file
# ═══════════════════════════════════════════════════════════════════════
def setup_logger() -> logging.Logger:
    """Cấu hình logger ghi WARNING/ERROR ra config.LOG_FILE."""
    logger = logging.getLogger("yt_downloader")
    logger.setLevel(logging.DEBUG)

    if config.LOG_FILE:
        Path(config.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(config.LOG_FILE, encoding="utf-8")
        fh.setLevel(logging.WARNING)
        fh.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
        logger.addHandler(fh)

    return logger

APP_LOG = setup_logger()


# ═══════════════════════════════════════════════════════════════════════
#  [FIX 1] YDL LOGGER — phát hiện video bị skip qua archive
# ═══════════════════════════════════════════════════════════════════════
class YdlLogger:
    """
    Custom logger inject vào yt-dlp để:
    - Bắt message "already been recorded" → đánh dấu was_skipped = True
    - Ghi warning/error ra APP_LOG
    """
    def __init__(self):
        self.was_skipped = False

    def debug(self, msg: str):
        # yt-dlp dùng debug() để thông báo "đã có trong archive"
        if "has already been recorded" in msg or "already been downloaded" in msg:
            self.was_skipped = True

    def warning(self, msg: str):
        APP_LOG.warning(msg)
        if config.VERBOSE:
            tqdm.write(f"  ⚠️  {msg}")

    def error(self, msg: str):
        APP_LOG.error(msg)
        if config.VERBOSE:
            tqdm.write(f"  ❌ {msg}")


# ═══════════════════════════════════════════════════════════════════════
#  [FIX 3] PREFLIGHT CHECK — kiểm tra môi trường trước khi tải
# ═══════════════════════════════════════════════════════════════════════
def preflight_check(format_type: str) -> None:
    """Kiểm tra ffmpeg, thư mục output. Thoát sớm nếu thiếu dependency."""
    print("\n🔧 Kiểm tra môi trường...")

    ffmpeg_ok = shutil.which("ffmpeg") is not None
    print(f"   ffmpeg  : {'✅ OK  (' + shutil.which('ffmpeg') + ')' if ffmpeg_ok else '❌ Không tìm thấy'}")

    if not ffmpeg_ok and format_type == "audio":
        print("\n❌ ffmpeg bắt buộc để chuyển đổi audio sang MP3.")
        print("   Cài đặt: brew install ffmpeg")
        sys.exit(1)

    if not ffmpeg_ok and format_type == "video":
        print("   ⚠️  Không có ffmpeg — video và audio sẽ không được merge.")

    print()


# ═══════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════
def format_duration(seconds: int | None) -> str:
    """Chuyển giây → mm:ss hoặc hh:mm:ss."""
    if not seconds:
        return "--:--"
    return str(timedelta(seconds=seconds))


# [FIX 2] Sanitize tên file — loại bỏ ký tự đặc biệt
def sanitize_title(title: str) -> str:
    """
    Làm sạch tiêu đề để dùng làm tên file an toàn trên mọi OS.
    Thay ký tự nguy hiểm và trim khoảng trắng/dấu chấm thừa.
    """
    replacements = {
        "/":  "-", "\\": "-", ":":  "-", "*":  "-",
        "?":  "",  '"':  "'", "<":  "",  ">":  "",
        "|":  "-", "｜": "-",  # full-width pipe
        "\n": " ", "\r": " ", "\t": " ",
    }
    for ch, rep in replacements.items():
        title = title.replace(ch, rep)

    # Bỏ ký tự điều khiển (ASCII < 32)
    title = "".join(c for c in title if ord(c) >= 32)

    # Không để tên file bắt đầu/kết thúc bằng dấu chấm hoặc space
    return title.strip(" .")


# ═══════════════════════════════════════════════════════════════════════
#  BƯỚC 1: Lấy danh sách video trong playlist
# ═══════════════════════════════════════════════════════════════════════
def fetch_playlist(url: str) -> dict:
    """Trả về metadata playlist (không tải video)."""
    ydl_opts = {
        "quiet":        True,
        "no_warnings":  True,
        "extract_flat": "in_playlist",
    }

    print(f"\n🔍 Đang tải thông tin playlist...")
    print(f"   URL: {url}\n")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    return info


# ═══════════════════════════════════════════════════════════════════════
#  BƯỚC 2: Hiển thị danh sách video
# ═══════════════════════════════════════════════════════════════════════
def display_playlist(info: dict) -> list[dict]:
    """In bảng danh sách video. Trả về list[dict] để download tiếp."""

    pl_title = info.get("title", "Không rõ")
    channel  = info.get("channel") or info.get("uploader", "Không rõ")
    entries  = info.get("entries", [])
    total    = len(entries)

    # Tách SKIP_VIDEOS thành 2 set: skip theo index (int) và theo ID (str)
    skip_indices = {v for v in config.SKIP_VIDEOS if isinstance(v, int)}
    skip_ids     = {v for v in config.SKIP_VIDEOS if isinstance(v, str)}

    print("=" * 70)
    print(f"  📋  {pl_title}")
    print(f"  👤  {channel}")
    print(f"  📦  Tổng số video: {total}")
    if skip_indices or skip_ids:
        print(f"  🚫  Bỏ qua (config): {len(skip_indices) + len(skip_ids)} video")
    print("=" * 70)

    if total == 0:
        print("  ⚠️  Playlist trống hoặc không thể truy cập.")
        return []

    print(f"  {'#':>4}  {'Tiêu đề':<48}  {'Thời lượng':>10}")
    print("  " + "-" * 66)

    videos = []
    user_skipped = 0

    for i, entry in enumerate(entries, start=1):
        if entry is None:
            print(f"  {i:>4}  {'[Video không khả dụng]':<48}  {'--:--':>10}")
            continue

        video_id  = entry.get("id", "")
        vid_title = entry.get("title") or f"video_{video_id}"
        duration  = format_duration(entry.get("duration"))
        url_video = entry.get("url") or f"https://youtube.com/watch?v={video_id}"

        # Kiểm tra video có nằm trong danh sách skip không
        is_skipped = (i in skip_indices) or (video_id in skip_ids)

        display_title = vid_title if len(vid_title) <= 48 else vid_title[:45] + "..."

        if is_skipped:
            user_skipped += 1
            print(f"  {i:>4}  {display_title:<48}  {duration:>10}  ⛔")
        else:
            print(f"  {i:>4}  {display_title:<48}  {duration:>10}")
            videos.append({
                "index": i,
                "id":    video_id,
                "title": sanitize_title(vid_title),   # [FIX 2] sanitize ngay khi đọc
                "url":   url_video,
            })

    print("  " + "-" * 66)
    msg = f"\n  ✅ Tìm thấy {len(videos)} video sẽ tải / {total} tổng."
    if user_skipped:
        msg += f"  (🚫 bỏ qua {user_skipped} video theo config)"
    print(msg + "\n")

    return videos


# ═══════════════════════════════════════════════════════════════════════
#  PROGRESS HOOK (tqdm)
# ═══════════════════════════════════════════════════════════════════════
def make_progress_hook(label: str):
    """Trả về yt-dlp progress hook dùng tqdm. Mỗi video có 1 bar riêng."""
    pbar: list[tqdm | None] = [None]

    def hook(d: dict):
        if d["status"] == "downloading":
            total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded  = d.get("downloaded_bytes", 0)
            speed       = d.get("_speed_str", "").strip()

            if pbar[0] is None:
                pbar[0] = tqdm(
                    total=total_bytes or None,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=label,
                    bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
                    ncols=80,
                    colour="green",
                    leave=True,
                )

            if pbar[0] is not None:
                if total_bytes:
                    pbar[0].total = total_bytes
                pbar[0].n = downloaded
                if speed:
                    pbar[0].set_postfix_str(speed, refresh=False)
                pbar[0].refresh()

        elif d["status"] == "finished":
            if pbar[0] is not None:
                pbar[0].n = pbar[0].total or pbar[0].n
                pbar[0].set_postfix_str("✔ xong", refresh=True)
                pbar[0].close()
                pbar[0] = None

        elif d["status"] == "error":
            if pbar[0] is not None:
                pbar[0].set_postfix_str("✘ lỗi", refresh=True)
                pbar[0].close()
                pbar[0] = None

    return hook


# ═══════════════════════════════════════════════════════════════════════
#  [FIX 4] BUILD BASE OPTIONS — tạo 1 lần, clone cho từng video
# ═══════════════════════════════════════════════════════════════════════
def build_base_opts(out_path: str, format_type: str) -> dict:
    """
    Tạo ydl_opts cơ sở từ config — KHÔNG có logger và progress_hook.
    Gọi 1 lần duy nhất trước vòng lặp, clone lại cho mỗi video.
    """
    if config.ARCHIVE_FILE:
        Path(config.ARCHIVE_FILE).parent.mkdir(parents=True, exist_ok=True)

    base = {
        "outtmpl":                 f"{out_path}/%(title)s.%(ext)s",
        "download_archive":        config.ARCHIVE_FILE,
        "retries":                 config.RETRIES,
        "fragment_retries":        config.FRAGMENT_RETRIES,
        "http_chunk_size":         config.HTTP_CHUNK_SIZE,
        "sleep_interval":          config.SLEEP_INTERVAL,
        "sleep_interval_requests": config.SLEEP_INTERVAL_MIN,
        "max_sleep_interval":      config.SLEEP_INTERVAL_MAX,
        "ratelimit":               config.RATE_LIMIT,
        "quiet":                   not config.VERBOSE,
        "no_warnings":             not config.VERBOSE,
        "ignoreerrors":            True,
    }

    if format_type == "audio":
        base.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key":              "FFmpegExtractAudio",
                "preferredcodec":   config.AUDIO_FORMAT,
                "preferredquality": config.AUDIO_QUALITY,
            }],
        })
    else:
        if config.RESOLUTION.lower() == "max":
            # Tải chất lượng cao nhất có sẵn — không giới hạn resolution
            base.update({
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "merge_output_format": config.VIDEO_FORMAT,
            })
        else:
            res = config.RESOLUTION.replace("p", "")   # "720p" → "720"
            base.update({
                "format": (
                    f"bestvideo[height<={res}][ext=mp4]+bestaudio[ext=m4a]"
                    f"/best[height<={res}][ext=mp4]"
                ),
                "merge_output_format": config.VIDEO_FORMAT,
            })

    return base


# ═══════════════════════════════════════════════════════════════════════
#  BƯỚC 3: Download toàn bộ playlist
# ═══════════════════════════════════════════════════════════════════════
def download_playlist(videos: list[dict], format_type: str = "video"):
    """
    Tải từng video trong playlist với:
    - [FIX 1] Đếm skip/success chính xác qua YdlLogger
    - [FIX 2] Tên file đã được sanitize
    - [FIX 3] Kiểm tra ffmpeg trước khi chạy
    - [FIX 4] base_opts build 1 lần, clone cho từng video
    - [FIX 5] Ghi lỗi ra LOG_FILE
    """
    if not videos:
        print("⚠️  Không có video nào để tải.")
        return

    # [FIX 3] Kiểm tra ffmpeg
    preflight_check(format_type)

    # Chuẩn bị thư mục output
    sub_dir  = config.AUDIO_SUBDIR if format_type == "audio" else config.VIDEO_SUBDIR
    out_path = str(Path(config.OUTPUT_DIR) / sub_dir)
    Path(out_path).mkdir(parents=True, exist_ok=True)

    total    = len(videos)
    ext_name = config.AUDIO_FORMAT.upper() if format_type == "audio" else config.VIDEO_FORMAT.upper()
    quality  = f"{config.AUDIO_QUALITY}kbps" if format_type == "audio" else (
        "MAX (cao nhất)" if config.RESOLUTION.lower() == "max" else config.RESOLUTION
    )

    print(f"{'─' * 70}")
    print(f"  🚀 Bắt đầu tải {total} file ({ext_name} · {quality})")
    print(f"  📁 Thư mục    : {out_path}")
    if config.ARCHIVE_FILE:
        print(f"  📒 Archive    : {config.ARCHIVE_FILE}  (bỏ qua nếu đã tải)")
    if config.LOG_FILE:
        print(f"  📝 Log lỗi   : {config.LOG_FILE}")
    print(f"{'─' * 70}\n")

    # [FIX 4] Build base opts 1 lần duy nhất
    base_opts = build_base_opts(out_path, format_type)

    success = 0
    skipped = 0
    failed  = 0

    for video in videos:
        idx   = video["index"]
        title = video["title"]
        url   = video["url"]

        short_title = title[:30] + "…" if len(title) > 30 else title
        label = f"  [{idx:>3}/{total}] {short_title:<31}"

        # [FIX 1] Logger + hook riêng cho từng video
        ydl_logger = YdlLogger()
        hook       = make_progress_hook(label)

        # Clone base_opts — không mutate dict gốc
        ydl_opts = {
            **base_opts,
            "logger":         ydl_logger,
            "progress_hooks": [hook],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # [FIX 1] Phân biệt skip vs success qua logger
            if ydl_logger.was_skipped:
                skipped += 1
                tqdm.write(f"  ⏭  [{idx}/{total}] Bỏ qua (đã tải): {title}")
            else:
                success += 1
                APP_LOG.info(f"OK [{idx}/{total}] {title}")

        except Exception as e:
            failed += 1
            msg = f"[{idx}/{total}] {title} — {e}"
            APP_LOG.error(msg)
            tqdm.write(f"  ❌ Lỗi: {msg}")

    # Summary
    print(f"\n{'=' * 70}")
    print(f"  🎉 Hoàn thành!")
    print(f"     ✅ Tải mới  : {success}")
    print(f"     ⏭  Bỏ qua  : {skipped}  (đã có trong archive)")
    print(f"     ❌ Lỗi     : {failed}")
    print(f"     📁 Lưu tại : {out_path}")
    if config.LOG_FILE and failed > 0:
        print(f"     📝 Xem log : {config.LOG_FILE}")
    print(f"{'=' * 70}\n")


# ═══════════════════════════════════════════════════════════════════════
#  CHỌN FORMAT
# ═══════════════════════════════════════════════════════════════════════
def ask_format() -> str:
    """Hỏi user muốn tải video hay audio."""
    print("  Chọn định dạng tải xuống:")
    print("    1. 📹  Video (MP4)")
    print("    2. 🎵  Audio (MP3)")
    print("    0. ❌  Thoát, không tải")

    while True:
        choice = input("\n  Lựa chọn (0/1/2): ").strip()
        if choice == "1":
            return "video"
        if choice == "2":
            return "audio"
        if choice == "0":
            return "cancel"
        print("  ⚠️  Vui lòng chọn 0, 1 hoặc 2.")


# ═══════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════
def main():
    url = sys.argv[1] if len(sys.argv) > 1 else config.PLAYLIST_URL

    try:
        info = fetch_playlist(url)
    except yt_dlp.utils.DownloadError as e:
        print(f"\n❌ Lỗi khi truy cập playlist:\n   {e}")
        APP_LOG.error(f"Playlist fetch error: {e}")
        sys.exit(1)

    videos = display_playlist(info)
    if not videos:
        sys.exit(0)

    fmt = ask_format()
    if fmt == "cancel":
        print("\n👋 Đã huỷ. Không tải file nào.")
        sys.exit(0)

    download_playlist(videos, format_type=fmt)


if __name__ == "__main__":
    main()
