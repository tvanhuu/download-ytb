.PHONY: setup run clean help

help: ## Hiển thị trợ giúp
	@echo "Các lệnh có sẵn:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Thiết lập môi trường
	@echo "Thiết lập môi trường..."
	@chmod +x setup.sh
	@./setup.sh

run: ## Chạy chương trình
	@echo "Chạy chương trình..."
	@chmod +x run.sh
	@./run.sh

clean: ## Dọn dẹp môi trường
	@echo "Dọn dẹp môi trường..."
	@rm -rf venv
	@echo "✅ Đã dọn dẹp xong!"

install: ## Cài đặt dependencies
	@echo "Cài đặt dependencies..."
	@pip install -r requirements.txt

test: ## Test chương trình
	@echo "Test chương trình..."
	@python -c "import requests; print('✅ Requests đã được cài đặt')"
