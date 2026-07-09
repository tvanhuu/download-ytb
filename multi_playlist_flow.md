# Flow: Tải nhiều playlist

## Tổng quan

```mermaid
flowchart TD
    START(["🚀 python main.py"]) --> GET["get_playlists()<br/>Đọc PLAYLISTS từ config"]
    GET --> CHECK{PLAYLISTS<br/>trống?}
    CHECK -->|Có| FALLBACK{"PLAYLIST_URL<br/>có giá trị?"}
    FALLBACK -->|Không| EXIT_ERR["❌ Thoát — không có playlist"]
    FALLBACK -->|Có| USE_OLD["Dùng PLAYLIST_URL<br/>fallback 1 playlist"]
    USE_OLD --> SHOW
    CHECK -->|Không| SHOW

    SHOW["📚 Hiển thị danh sách playlist<br/>1. ma-thien-ky<br/>2. pham-nhan-tu-tien<br/>3. tien-nghich"]
    SHOW --> ASK["ask_format()<br/>Hỏi 1 LẦN DUY NHẤT:<br/>Video / Audio / Huỷ?"]
    ASK -->|Huỷ| EXIT_CANCEL["👋 Thoát"]
    ASK -->|Video hoặc Audio| LOOP

    subgraph LOOP["🔄 Vòng lặp từng playlist"]
        direction TB
        PL_START["📋 PLAYLIST i / N"] --> FETCH["fetch_playlist(url)<br/>Lấy metadata"]
        FETCH -->|Lỗi| SKIP_PL["⏭ Bỏ qua playlist này<br/>→ tiếp playlist kế"]
        FETCH -->|OK| MERGE["Merge skip:<br/>global SKIP_VIDEOS<br/>+ playlist skip riêng"]
        MERGE --> DISPLAY["display_playlist()<br/>Hiển thị + lọc video"]
        DISPLAY -->|0 video| SKIP_PL2["⏭ Không có video<br/>→ tiếp playlist kế"]
        DISPLAY -->|Có video| DL["download_playlist()<br/>Tải vào thư mục riêng"]
        
        DL --> DOWNLOAD_EACH

        subgraph DOWNLOAD_EACH["⬇️ Tải từng video"]
            direction TB
            V_START["Video j / M"] --> V_DL["_download_single()"]
            V_DL --> V_CHECK{Kết quả?}
            V_CHECK -->|"✅ success"| V_NEXT["Video tiếp theo"]
            V_CHECK -->|"⏭ skipped"| V_NEXT
            V_CHECK -->|"❌ failed"| V_FAIL["Thêm vào failed list"]
            V_FAIL --> V_NEXT
        end

        DOWNLOAD_EACH --> RETRY{Có video<br/>failed?}
        RETRY -->|Có| RETRY_LOOP["🔄 Auto-retry<br/>tối đa N vòng"]
        RETRY_LOOP --> REPORT
        RETRY -->|Không| REPORT["📊 Verification Report<br/>cho playlist này"]
        
        REPORT --> NEXT_PL["→ Playlist tiếp theo"]
    end

    LOOP --> DONE["🎉 HOÀN THÀNH TẤT CẢ PLAYLIST!"]
```

## Ví dụ cụ thể với 3 playlist

```mermaid
flowchart LR
    subgraph CONFIG["📝 config.py"]
        P1["1. ma-thien-ky<br/>skip: 24 video"]
        P2["2. pham-nhan-tu-tien<br/>skip: none"]
        P3["3. tien-nghich<br/>skip: none"]
    end

    ASK["🎵 User chọn: Audio MP3"]

    subgraph RUN["🔄 Chạy tuần tự"]
        direction TB
        R1["📋 1/3: ma-thien-ky<br/>→ downloads/audio/ma-thien-ky/"]
        R2["📋 2/3: pham-nhan-tu-tien<br/>→ downloads/audio/pham-nhan-tu-tien/"]
        R3["📋 3/3: tien-nghich<br/>→ downloads/audio/tien-nghich/"]
        R1 --> R2 --> R3
    end

    CONFIG --> ASK --> RUN

    RUN --> DONE["🎉 Hoàn thành 3 playlist!"]
```

## Cấu trúc thư mục output

```
downloads/
├── audio/
│   ├── ma-thien-ky/          ← Playlist 1
│   │   ├── Chương 001.mp3
│   │   ├── Chương 002.mp3
│   │   └── ...
│   ├── pham-nhan-tu-tien/    ← Playlist 2
│   │   ├── Tập 001.mp3
│   │   └── ...
│   └── tien-nghich/          ← Playlist 3
│       ├── Tập 001.mp3
│       └── ...
├── archive.txt               ← Chung cho tất cả (skip video đã tải)
└── error.log                 ← Log lỗi chung
```

> [!NOTE]
> - **Hỏi format 1 lần** → áp dụng cho tất cả playlist
> - **Mỗi playlist lỗi** → bỏ qua, không dừng cả script
> - **Archive chung** → video đã tải ở playlist nào cũng được skip
> - **Skip merge** = `SKIP_VIDEOS` global + `skip` riêng từng playlist
