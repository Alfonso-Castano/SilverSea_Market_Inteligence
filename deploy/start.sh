#!/bin/bash
# Silversea Market Intelligence — Gunicorn 启动/重启脚本
# 用法: bash deploy/start.sh

set -e

PROJECT_DIR="/www/wwwroot/ai-mi"
VENV_DIR="$PROJECT_DIR/im-env"
PID_FILE="$PROJECT_DIR/gunicorn.pid"
LOG_FILE="$PROJECT_DIR/gunicorn.log"
BIND="127.0.0.1:8001"
WORKERS=4
TIMEOUT=120

# 检查项目目录是否存在
if [ ! -d "$PROJECT_DIR" ]; then
    echo "错误: 项目目录不存在 — $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

# 激活虚拟环境
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "错误: 虚拟环境不存在 — $VENV_DIR"
    exit 1
fi
source "$VENV_DIR/bin/activate"

# 如果已运行则先停止
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "发现运行中的 Gunicorn (PID: $OLD_PID)，正在停止..."
        kill "$OLD_PID"
        sleep 2

        # 如果未退出则强制终止
        if kill -0 "$OLD_PID" 2>/dev/null; then
            echo "进程未响应，强制终止..."
            kill -9 "$OLD_PID"
            sleep 1
        fi
        echo "已停止旧进程。"
    else
        echo "PID 文件存在但进程已不存在，清理后重新启动。"
    fi
    rm -f "$PID_FILE"
fi

# 后台启动 Gunicorn（--daemon 自动后台化并写入 PID 文件）
echo "正在启动 Gunicorn..."
gunicorn \
    --bind "$BIND" \
    --workers "$WORKERS" \
    --timeout "$TIMEOUT" \
    --pid "$PID_FILE" \
    --daemon \
    --access-logfile "$LOG_FILE" \
    --error-logfile "$LOG_FILE" \
    app:app

# 等待 PID 文件生成
sleep 2

if [ -f "$PID_FILE" ]; then
    NEW_PID=$(cat "$PID_FILE")
    if kill -0 "$NEW_PID" 2>/dev/null; then
        echo "Gunicorn 启动成功 (PID: $NEW_PID)"
        echo "监听地址: $BIND"
        echo "日志文件: $LOG_FILE"
    else
        echo "错误: PID 文件存在但进程未运行，请检查日志: $LOG_FILE"
        exit 1
    fi
else
    echo "错误: PID 文件未生成，请检查日志: $LOG_FILE"
    exit 1
fi
