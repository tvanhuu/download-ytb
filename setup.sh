#!/bin/bash

echo "=== Thiết lập môi trường cho Copy Trade ==="

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 không được cài đặt. Vui lòng cài đặt Python3 trước."
    exit 1
fi

echo "✅ Python3 đã được cài đặt: $(python3 --version)"

# Tạo virtual environment
echo "📦 Tạo virtual environment..."
python3 -m venv venv

# Kích hoạt virtual environment
echo "🔧 Kích hoạt virtual environment..."
source venv/bin/activate

# Cài đặt dependencies
echo "📥 Cài đặt dependencies..."
pip install -r requirements.txt

echo "✅ Thiết lập hoàn tất!"
echo ""
echo "Các thư viện đã cài đặt:"
echo "yt_dlp: Tải video từ YouTube"
echo "shutil: Tải audio từ YouTube"
echo ""
echo "Để chạy chương trình:"
echo "1. Kích hoạt môi trường: source venv/bin/activate"
echo "2. Chạy chương trình: python download_yt.py"
echo ""
echo "Hoặc chạy trực tiếp: ./run.sh"
