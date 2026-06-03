from pathlib import Path
import yt_dlp
import shutil


def download_youtube_video(
    video_ids,
    output_path=None,
    resolution="720p",
    format_type="video",
    title_videos=None,
    default_url=True,
):
    for index, video_id in enumerate(video_ids, 1):
        try:
            url = (
                f"https://www.youtube.com/watch?v={video_id}"
                if default_url
                else video_id
            )

            title = (
                title_videos[index - 1]
                if title_videos
                and len(title_videos) >= index
                and title_videos[index - 1] != ""
                else None
            )

            # Tạo template cho tên file dựa vào title_videos nếu có
            output_template = (
                f"{output_path}/{title}.%(ext)s"
                if title
                else (
                    f"{output_path}/%(title)s.%(ext)s"
                    if output_path
                    else "%(title)s.%(ext)s"
                )
            )

            # Cấu hình tùy chọn dựa vào format_type
            if format_type == "audio":
                ydl_opts = {
                    "format": "bestaudio/best",
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }
                    ],
                    "outtmpl": output_template,
                    "progress_hooks": [
                        lambda d: print(
                            f'Đang tải: {d["_percent_str"]} của {d["_total_bytes_str"]}'
                        )
                    ],
                }
            else:
                ydl_opts = {
                    "format": f"bestvideo[height<={resolution[:-1]}][ext=mp4]+bestaudio[ext=m4a]/best[height<={resolution[:-1]}][ext=mp4]",
                    "merge_output_format": "mp4",
                    "outtmpl": output_template,
                    "progress_hooks": [
                        lambda d: print(
                            f'Đang tải: {d["_percent_str"]} của {d["_total_bytes_str"]}'
                        )
                    ],
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])  # Tải từng URL một

            print(f"Video {index} đã tải xuống thành công!")

        except Exception as e:
            print(f"Có lỗi khi tải video {index}:")
            print(f"Lỗi: {str(e)}")
            print("Chi tiết lỗi:", e.__class__.__name__)
            continue  # Tiếp tục với video tiếp theo nếu có lỗi

    print("\nĐã hoàn thành tất cả các video!")


def download_youtube_audio(
    video_urls, output_path=None, check_path=None, titles=None, default_url=True
):
    """
    Download audio (MP3) from YouTube videos, skipping if file already exists

    Args:
        video_urls: str or List[str] - YouTube video URL(s) or video ID(s)
        output_path: str - Output directory path (optional)
        check_path: str - Directory to check for existing files (optional)
        titles: List[str] - Custom titles for the audio files (optional)
        default_url: bool - If True, treats video_urls as video IDs and constructs full URLs
    """
    # Convert single URL to list
    if isinstance(video_urls, str):
        video_urls = [video_urls]

    # Convert single title to list
    if titles and isinstance(titles, str):
        titles = [titles]

    # Create output directory if it doesn't exist
    if output_path:
        Path(output_path).mkdir(parents=True, exist_ok=True)

    # Get list of existing files in output directory
    existing_files = []
    if output_path:
        existing_files = [
            f.stem
            for f in Path(check_path if check_path else output_path).glob("*.mp3")
        ]
    for index, video_url in enumerate(video_urls):
        try:
            # Construct URL if video ID is provided
            url = (
                f"https://www.youtube.com/watch?v={video_url}"
                if default_url
                else video_url
            )

            # Set output template
            title = titles[index] if titles and len(titles) > index else None

            # Set output template for download
            output_template = (
                f"{output_path}/{title}.%(ext)s"
                if title and output_path
                else (
                    f"{output_path}/%(title)s.%(ext)s"
                    if output_path
                    else "%(title)s.%(ext)s"
                )
            )

            ydl_opts = {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "outtmpl": output_template,
                "progress_hooks": [
                    lambda d: print(
                        f'Downloading: {d["_percent_str"]} of {d["_total_bytes_str"]}'
                    )
                ],
                # Thêm các cấu hình này:
                "extract_flat": False,
                "no_warnings": False,
                "ignoreerrors": False,
                "retries": 3,
                "fragment_retries": 3,
                "http_chunk_size": 10485760,  # 10MB
                "sleep_interval": 1,  # Nghỉ 1 giây giữa các request
            }

            # Configure yt-dlp options to get video info first
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                video_info = ydl.extract_info(url, download=False)
                video_title = title or video_info["title"]

                # Replace special characters ｜ and | with -
                video_title = video_title.replace("｜", "-").replace("|", "-")

                title = video_title
                # Check if file already exists
                if video_title in existing_files:
                    print(f"Skipping '{video_title}' - File already exists")
                    continue

                ydl.download([url])

            # Get the actual downloaded file path
            downloaded_file = Path(output_path) / f"{title}.mp3"
            if check_path and output_path != check_path:
                Path(check_path).mkdir(parents=True, exist_ok=True)
                shutil.copy2(downloaded_file, check_path)
                print(f"File copied FROM {output_path} TO {check_path}")

            print(f"Audio {index + 1} downloaded successfully!")

        except Exception as e:
            print(f"Error downloading audio {index + 1}:")
            print(f"Error: {str(e)}")
            print("Error details:", e.__class__.__name__)
            continue

    print("\nAll audio downloads completed!")


def clear_screen():
    """Function xóa màn hình"""
    import os

    os.system("cls" if os.name == "nt" else "clear")


def download_video_loop():
    """Function tải video liên tục"""
    print("\n=== 📹 TẢI VIDEO ===")
    print("Nhập 'quit' để quay lại menu chính")

    while True:
        url = input("\n Nhập link YouTube: ").strip()

        if url.lower() == "quit":
            break

        if not url:
            print("❌ Vui lòng nhập link!")
            continue

        # Tạo thư mục downloads nếu chưa có
        output_path = "downloads/videos"
        Path(output_path).mkdir(parents=True, exist_ok=True)

        try:
            download_youtube_video(
                [url],
                output_path=output_path,
                resolution="720p",
                format_type="video",
                default_url=False,
            )
            print("✅ Tải video thành công!")
        except Exception as e:
            print(f"❌ Lỗi khi tải video: {e}")


def download_audio_loop():
    """Function tải audio liên tục"""
    print("\n=== 🎵 TẢI AUDIO ===")
    print("Nhập 'quit' để quay lại menu chính")

    while True:
        url = input("\n Nhập link YouTube: ").strip()

        if url.lower() == "quit":
            break

        if not url:
            print("❌ Vui lòng nhập link!")
            continue

        # Tạo thư mục downloads nếu chưa có
        output_path = "downloads/audio"
        Path(output_path).mkdir(parents=True, exist_ok=True)

        try:
            download_youtube_audio(
                [url],
                output_path=output_path,
                check_path=output_path,
                default_url=False,
            )
            print("✅ Tải audio thành công!")
        except Exception as e:
            print(f"❌ Lỗi khi tải audio: {e}")


def main():
    """Function chính để chạy chương trình"""
    while True:
        clear_screen()
        print("===  YOUTUBE DOWNLOADER ===")
        print("1. 📹 Tải video")
        print("2.  Tải audio (MP3)")
        print("3. ❌ Thoát chương trình")

        choice = input("\nChọn chức năng (1-3): ").strip()

        if choice == "1":
            download_video_loop()
        elif choice == "2":
            download_audio_loop()
        elif choice == "3":
            print("👋 Tạm biệt!")
            break
        else:
            print("❌ Lựa chọn không hợp lệ!")
            input("Nhấn Enter để tiếp tục...")


if __name__ == "__main__":
    main()
