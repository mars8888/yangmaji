#!/bin/bash
# Chrome 启动脚本（WSL环境）
google-chrome \
  --no-sandbox \
  --remote-debugging-port=9222 \
  --user-data-dir=~/.chrome-debug &

echo "Chrome 已启动，调试端口: 9222"
