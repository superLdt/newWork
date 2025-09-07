# Makefile for Smart Transport System Development

.PHONY: help guard test lint format

# Default target
help:
	@echo "可用命令:"
	@echo "  make guard      - 运行架构检查"
	@echo "  make guard-strict - 严格模式架构检查"
	@echo "  make test       - 运行测试"
	@echo "  make lint       - 代码质量检查"
	@echo "  make format     - 代码格式化"
	@echo "  make dev        - 启动开发环境"

# Architecture guard checks
guard:
	@echo "🔍 运行架构检查..."
	python scripts/architecture_guard.py

guard-strict:
	@echo "🔍 运行严格模式架构检查..."
	python scripts/architecture_guard.py --strict

guard-module:
	@if [ -z "$(module)" ]; then \
		echo "请指定模块: make guard-module module=dispatch"; \
		false; \
	fi
	@echo "🔍 检查模块 $(module)..."
	python scripts/architecture_guard.py --module $(module)

# Testing
test:
	@echo "🧪 运行测试..."
	cd backend && python -m pytest -v

# Linting
lint:
	@echo "📏 运行代码检查..."
	cd backend && python -m flake8 app --max-line-length=88 --statistics

# Formatting
format:
	@echo "🎨 代码格式化..."
	cd backend && python -m black app --line-length=88
	cd backend && python -m isort app

# Development environment
dev:
	@echo "🚀 启动开发环境..."
	# 添加开发环境启动命令

# Clean
clean:
	@echo "🧹 清理临时文件..."
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	find . -name "*.pyo" -delete