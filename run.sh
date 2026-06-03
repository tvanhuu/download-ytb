#!/bin/bash

echo "=== Chạy Copy Trade ==="

# Kiểm tra virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment chưa được tạo."
    echo "Vui lòng chạy: ./setup.sh trước."
    exit 1
fi

# Kích hoạt virtual environment
echo "🔧 Kích hoạt virtual environment..."
source venv/bin/activate

# Chạy chương trình
echo "🚀 Khởi chạy chương trình..."
python3 download_yt.py

# Deactivate virtual environment
deactivate
echo "✅ Hoàn tất!"
