import os
import platform
import shutil
import yt_dlp
import logging
from pathlib import Path
from datetime import timedelta
from tqdm import tqdm
import sys
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


import config

# Tự động sửa/thêm PATH trên Windows nếu chưa nhận diện được ffmpeg
if platform.system() == "Windows":
    paths = []
    
    # 1. Đọc từ Registry (User)
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            user_path = winreg.QueryValueEx(key, "Path")[0]
            for p in user_path.split(";"):
                p = os.path.expandvars(p.strip())
                if p:
                    paths.append(p)
    except Exception:
        pass

    # 2. Đọc từ Registry (Machine)
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"System\CurrentControlSet\Control\Session Manager\Environment") as key:
            machine_path = winreg.QueryValueEx(key, "Path")[0]
            for p in machine_path.split(";"):
                p = os.path.expandvars(p.strip())
                if p:
                    paths.append(p)
    except Exception:
        pass

    # 3. Thêm PATH hiện tại
    for p in os.environ.get("PATH", "").split(os.path.pathsep):
        p = p.strip()
        if p:
            paths.append(p)

    # 4. Thêm các đường dẫn mặc định phổ biến
    common_paths = [
        r"D:\ffmpeg-latest\bin",
        r"C:\ffmpeg\bin"
    ]
    for cp in common_paths:
        if os.path.exists(cp):
            paths.append(cp)

    # Làm sạch và chuẩn hoá các đường dẫn
    seen = set()
    cleaned_paths = []
    for p in paths:
        if p.lower().endswith(".exe"):
            p = os.path.dirname(p)
        try:
            p = os.path.abspath(p)
            if os.path.isdir(p) and p.lower() not in seen:
                seen.add(p.lower())
                cleaned_paths.append(p)
        except Exception:
            pass

    os.environ["PATH"] = os.path.pathsep.join(cleaned_paths)
    



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
#  CUSTOM PLAYLIST PARSER FOR NEW LAYOUTS (lockupViewModel)
# ═══════════════════════════════════════════════════════════════════════
import urllib.request
import re
import json
from datetime import datetime

def parse_duration(duration_str: str | None) -> int | None:
    if not duration_str:
        return None
    parts = duration_str.split(':')
    try:
        parts = [int(p) for p in parts]
        if len(parts) == 1:
            return parts[0]
        elif len(parts) == 2:
            return parts[0] * 60 + parts[1]
        elif len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
    except Exception:
        pass
    return None

def find_keys(d, target_key, results=None):
    if results is None:
        results = []
    if isinstance(d, dict):
        for k, v in d.items():
            if k == target_key:
                results.append(v)
            else:
                find_keys(v, target_key, results)
    elif isinstance(d, list):
        for item in d:
            find_keys(item, target_key, results)
    return results

def get_continuation_token(data_dict):
    continuations = find_keys(data_dict, 'continuationItemViewModel')
    if continuations:
        token = (continuations[0]
                 .get('continuationCommand', {})
                 .get('innertubeCommand', {})
                 .get('continuationCommand', {})
                 .get('token'))
        return token
    return None

def extract_video_info(lockup_vm):
    try:
        title = (lockup_vm
                 .get('metadata', {})
                 .get('lockupMetadataViewModel', {})
                 .get('title', {})
                 .get('content'))
        video_id = lockup_vm.get('contentId')
        
        duration_text = None
        overlays = lockup_vm.get('contentImage', {}).get('thumbnailViewModel', {}).get('overlays', [])
        for overlay in overlays:
            badge = overlay.get('thumbnailBottomOverlayViewModel', {}).get('badges', [])
            if badge:
                duration_text = badge[0].get('thumbnailBadgeViewModel', {}).get('text')
                break
                
        duration_sec = parse_duration(duration_text)
        
        return {
            'id': video_id,
            'title': title,
            'duration': duration_sec,
            'url': f"https://youtube.com/watch?v={video_id}"
        }
    except Exception:
        return None

def fetch_playlist_custom(url: str) -> dict | None:
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        )
        html = urllib.request.urlopen(req).read().decode('utf-8')
        
        # 1. Find API key
        api_key_match = re.search(r'AIzaSy[A-Za-z0-9_-]{33,40}', html)
        api_key = api_key_match.group(0) if api_key_match else None
        if not api_key:
            return None
            
        # 2. Extract ytInitialData
        pattern = re.compile(r'window\["ytInitialData"\]\s*=\s*({.*?});|ytInitialData\s*=\s*({.*?});', re.DOTALL)
        match = pattern.search(html)
        if not match:
            return None
            
        data_str = match.group(1) or match.group(2)
        data = json.loads(data_str)
        
        # 3. Check if this is a new layout playlist using lockupViewModel
        lockups = find_keys(data, 'lockupViewModel')
        if not lockups:
            return None # Fallback to standard yt-dlp
            
        print(f"   [Custom Extractor] Phát hiện playlist cấu trúc mới (lockupViewModel). Đang tải...")
        
        # Extract title and channel info
        pl_title = "Không rõ"
        pmr = find_keys(data, 'playlistMetadataRenderer')
        if pmr:
            pl_title = pmr[0].get('title', 'Không rõ')
            
        channel = "Không rõ"
        vor = find_keys(data, 'videoOwnerRenderer')
        if vor:
            runs = vor[0].get('title', {}).get('runs', [])
            if runs:
                channel = runs[0].get('text', 'Không rõ')
                
        entries = []
        for lockup in lockups:
            info = extract_video_info(lockup)
            if info:
                entries.append(info)
                
        # Get next continuation token
        token = get_continuation_token(data)
        
        # Generate dynamic client version based on current date
        current_date_str = datetime.now().strftime("%Y%m%d")
        client_version = f"2.{current_date_str}.00.00"
        
        page = 1
        while token:
            browse_url = f"https://www.youtube.com/youtubei/v1/browse?key={api_key}"
            payload = {
                "context": {
                    "client": {
                        "clientName": "WEB",
                        "clientVersion": client_version
                    }
                },
                "continuation": token
            }
            
            post_data = json.dumps(payload).encode('utf-8')
            post_req = urllib.request.Request(
                browse_url,
                data=post_data,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
            )
            
            try:
                res = urllib.request.urlopen(post_req).read().decode('utf-8')
                res_json = json.loads(res)
                
                page_lockups = find_keys(res_json, 'lockupViewModel')
                if not page_lockups:
                    break
                    
                page_entries_count = 0
                for lockup in page_lockups:
                    info = extract_video_info(lockup)
                    if info:
                        entries.append(info)
                        page_entries_count += 1
                
                # Check for next continuation token
                token = get_continuation_token(res_json)
                page += 1
            except Exception as e:
                APP_LOG.warning(f"Error fetching page {page} of playlist continuation: {e}")
                break
                
        return {
            "title": pl_title,
            "channel": channel,
            "uploader": channel,
            "entries": entries
        }
    except Exception as e:
        APP_LOG.warning(f"Custom playlist extractor failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════
#  BƯỚC 1: Lấy danh sách video trong playlist
# ═══════════════════════════════════════════════════════════════════════
def fetch_playlist(url: str) -> dict:
    """Trả về metadata playlist (không tải video)."""
    print(f"\n🔍 Đang tải thông tin playlist...")
    print(f"   URL: {url}\n")
    
    # Thử cào bằng parser tuỳ chỉnh hỗ trợ lockupViewModel
    info = fetch_playlist_custom(url)
    if info:
        return info

    # Fallback về yt-dlp mặc định nếu không phải cấu trúc mới hoặc cào lỗi
    ydl_opts = {
        "quiet":        True,
        "no_warnings":  True,
        "extract_flat": "in_playlist",
    }

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
        # ── Subtitle mode ──
        sub_mode = config.SUBTITLE_MODE.lower()
        sub_langs = config.SUBTITLE_LANGS

        if sub_mode == "only":
            # Chỉ tải phụ đề — không tải video
            base.update({
                "skip_download":      True,
                "writesubtitles":     True,
                "writeautomaticsub":  True,
                "subtitleslangs":     sub_langs.split(","),
                "subtitlesformat":    "srt/ass/vtt/best",
            })
            return base

        # ── Video format ──
        if config.RESOLUTION.lower() == "max":
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

        # ── Embed subtitle vào video ──
        if sub_mode == "embed":
            base.update({
                "writesubtitles":     True,
                "writeautomaticsub":  True,
                "subtitleslangs":     sub_langs.split(","),
                "subtitlesformat":    "srt/ass/vtt/best",
                "postprocessors":     base.get("postprocessors", []) + [
                    {
                        "key": "FFmpegSubtitlesConvertor",
                        "format": "srt",
                    },
                    {
                        "key": "FFmpegEmbedSubtitle",
                    },
                ],
            })

        # ── Tải video + phụ đề riêng (2 file tách biệt) ──
        elif sub_mode == "separate":
            base.update({
                "writesubtitles":     True,
                "writeautomaticsub":  True,
                "subtitleslangs":     sub_langs.split(","),
                "subtitlesformat":    "srt/ass/vtt/best",
            })

    return base


# ═══════════════════════════════════════════════════════════════════════
#  [FIX 6] HELPERS — verify & retry
# ═══════════════════════════════════════════════════════════════════════
def _get_dir_files(directory: str) -> set[str]:
    """Lấy danh sách file trong thư mục (không đệ quy, bỏ qua thư mục con)."""
    try:
        return {
            f for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))
        }
    except OSError:
        return set()


def _download_single(
    video: dict,
    base_opts: dict,
    out_path: str,
    total: int,
    attempt: int = 1,
) -> str:
    """
    Tải 1 video và verify kết quả.

    Returns:
        "success" — tải thành công, file thực sự tồn tại
        "skipped" — đã có trong archive
        "failed"  — lỗi hoặc file không được tạo (silent failure)
    """
    idx   = video["index"]
    title = video["title"]
    url   = video["url"]

    attempt_label = f" (lần {attempt})" if attempt > 1 else ""
    short_title = title[:30] + "…" if len(title) > 30 else title
    label = f"  [{idx:>3}/{total}] {short_title:<31}{attempt_label}"

    # Logger + hook riêng cho từng video
    ydl_logger = YdlLogger()
    hook       = make_progress_hook(label)

    ydl_opts = {
        **base_opts,
        "logger":         ydl_logger,
        "progress_hooks": [hook],
    }

    # ── [MỨC 1] Snapshot thư mục TRƯỚC khi tải ──
    files_before = _get_dir_files(out_path)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Phân biệt skip vs success
        if ydl_logger.was_skipped:
            tqdm.write(f"  ⏭  [{idx}/{total}] Bỏ qua (đã tải): {title}")
            return "skipped"

        # ── [MỨC 1] Verify file thực sự được tạo ──
        files_after = _get_dir_files(out_path)
        new_files = files_after - files_before

        if new_files:
            APP_LOG.info(f"OK [{idx}/{total}] {title}")
            return "success"
        else:
            # yt-dlp return OK nhưng KHÔNG tạo file → silent failure
            msg = f"[{idx}/{total}] {title} — File không được tạo (yt-dlp lỗi âm thầm)"
            APP_LOG.warning(msg)
            tqdm.write(f"  ⚠️  {msg}")
            return "failed"

    except Exception as e:
        msg = f"[{idx}/{total}] {title} — {e}"
        APP_LOG.error(msg)
        tqdm.write(f"  ❌ Lỗi: {msg}")
        return "failed"


def _print_verification(
    videos: list[dict],
    results: dict[str, str],
    failed_videos: list[dict],
    out_path: str,
):
    """
    [MỨC 3] Báo cáo verification cuối cùng.
    So sánh danh sách video cần tải vs kết quả thực tế.
    In URL của video thiếu để dễ tải lại thủ công.
    """
    total_videos   = len(videos)
    count_success  = sum(1 for s in results.values() if s == "success")
    count_skipped  = sum(1 for s in results.values() if s == "skipped")
    count_failed   = sum(1 for s in results.values() if s == "failed")
    count_verified = count_success + count_skipped  # file tồn tại (mới tải + đã có)

    print(f"\n{'═' * 70}")
    print(f"  📊 VERIFICATION REPORT")
    print(f"{'═' * 70}")
    print(f"     📦 Tổng cần tải  : {total_videos}")
    print(f"     ✅ Thành công    : {count_success}")
    print(f"     ⏭  Đã có (skip) : {count_skipped}")
    print(f"     ❌ Thất bại      : {count_failed}")
    print(f"     📁 Thư mục      : {out_path}")

    if failed_videos:
        print(f"\n  {'─' * 66}")
        print(f"  ⚠️  CÁC VIDEO BỊ THIẾU ({len(failed_videos)} video):")
        print(f"  {'─' * 66}")
        for v in failed_videos:
            short = v['title'][:50] + '…' if len(v['title']) > 50 else v['title']
            print(f"     ❌ [{v['index']}] {short}")
            print(f"        URL: {v['url']}")
        print(f"  {'─' * 66}")
        print(f"  💡 Chạy lại script để tải các video thiếu (archive sẽ skip video đã có).")
    else:
        print(f"\n  ✅ HOÀN HẢO! Tất cả {count_verified} video đều đã được tải/có sẵn.")

    print(f"{'═' * 70}\n")


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
    - [FIX 6] Verify file tồn tại + auto-retry + verification report
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

    # Subtitle mode label
    sub_mode = config.SUBTITLE_MODE.lower() if format_type == "video" else None
    sub_labels = {"none": None, "embed": "📝 nhúng vào video", "separate": "📝 file riêng", "only": "📝 chỉ phụ đề"}
    sub_label = sub_labels.get(sub_mode)

    print(f"{'─' * 70}")
    if sub_mode == "only":
        print(f"  🚀 Bắt đầu tải phụ đề cho {total} video ({config.SUBTITLE_LANGS})")
    else:
        print(f"  🚀 Bắt đầu tải {total} file ({ext_name} · {quality})")
    if sub_label:
        print(f"  📝 Phụ đề    : {sub_label}  (ngôn ngữ: {config.SUBTITLE_LANGS})")
    print(f"  📁 Thư mục    : {out_path}")
    if config.ARCHIVE_FILE:
        print(f"  📒 Archive    : {config.ARCHIVE_FILE}  (bỏ qua nếu đã tải)")
    if config.LOG_FILE:
        print(f"  📝 Log lỗi   : {config.LOG_FILE}")
    if config.MAX_DOWNLOAD_RETRIES > 0:
        print(f"  🔄 Auto-retry : tối đa {config.MAX_DOWNLOAD_RETRIES} vòng cho video lỗi")
    print(f"{'─' * 70}\n")

    # [FIX 4] Build base opts 1 lần duy nhất
    base_opts = build_base_opts(out_path, format_type)

    # ── Lượt tải chính ──
    results: dict[str, str] = {}   # video_id → "success" | "skipped" | "failed"
    failed_videos: list[dict] = []

    for video in videos:
        status = _download_single(video, base_opts, out_path, total)
        results[video["id"]] = status
        if status == "failed":
            failed_videos.append(video)

    # ── [MỨC 2] Auto-retry cho video thất bại ──
    retry_round = 0
    while failed_videos and retry_round < config.MAX_DOWNLOAD_RETRIES:
        retry_round += 1
        print(f"\n{'─' * 70}")
        print(f"  🔄 RETRY lần {retry_round}/{config.MAX_DOWNLOAD_RETRIES}")
        print(f"     📋 {len(failed_videos)} video cần thử lại")
        print(f"{'─' * 70}\n")

        still_failed: list[dict] = []
        for video in failed_videos:
            status = _download_single(
                video, base_opts, out_path, total,
                attempt=retry_round + 1,
            )
            results[video["id"]] = status
            if status == "failed":
                still_failed.append(video)

        recovered = len(failed_videos) - len(still_failed)
        if recovered > 0:
            tqdm.write(f"  ✅ Retry lần {retry_round}: phục hồi {recovered} video")

        failed_videos = still_failed

        if not failed_videos:
            tqdm.write(f"  🎉 Retry thành công! Tất cả video đã được tải.")
            break

    # Đếm kết quả cuối cùng
    success = sum(1 for s in results.values() if s == "success")
    skipped = sum(1 for s in results.values() if s == "skipped")
    failed  = sum(1 for s in results.values() if s == "failed")

    # Summary
    print(f"\n{'=' * 70}")
    print(f"  🎉 Hoàn thành!")
    print(f"     ✅ Tải mới  : {success}")
    print(f"     ⏭  Bỏ qua  : {skipped}  (đã có trong archive)")
    print(f"     ❌ Lỗi     : {failed}")
    print(f"     📁 Lưu tại : {out_path}")
    if config.LOG_FILE and failed > 0:
        print(f"     📝 Xem log : {config.LOG_FILE}")
    print(f"{'=' * 70}")

    # ── [MỨC 3] Verification report ──
    _print_verification(videos, results, failed_videos, out_path)


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
