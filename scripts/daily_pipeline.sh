#!/bin/bash
# Silversea Market Intelligence — daily pipeline + archival entrypoint (aaPanel scheduled task)
# 用法: bash scripts/daily_pipeline.sh

set -e

PROJECT_DIR="/www/wwwroot/ai-mi"
VENV_DIR="$PROJECT_DIR/im-env"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "错误: 项目目录不存在 — $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "错误: 虚拟环境不存在 — $VENV_DIR"
    exit 1
fi
source "$VENV_DIR/bin/activate"

python scripts/daily_pipeline.py
