#!/bin/bash
# OpenCLI WSL 环境安装与配置脚本
# 养马记03 配套脚本：WSL 下的 OpenCLI 应用
# 用法: bash setup_opencli.sh

set -e

echo "=== OpenCLI WSL 环境配置 ==="

# 1. 安装 Node.js (如果未安装)
if ! command -v node &> /dev/null; then
    echo "[1/5] 安装 Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    echo "[1/5] Node.js 已安装: $(node -v)"
fi

# 2. 安装 OpenCLI
echo "[2/5] 安装 OpenCLI..."
npm install -g @jackwener/opencli

# 3. 安装中文字体 (解决截图乱码)
echo "[3/5] 安装中文字体..."
sudo apt-get install -y fonts-noto-cjk fonts-wqy-zenhei
fc-cache -fv

# 4. 安装 Google Chrome (如果未安装)
if ! command -v google-chrome &> /dev/null; then
    echo "[4/5] 安装 Google Chrome..."
    wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo apt-get install -y /tmp/chrome.deb
    rm /tmp/chrome.deb
else
    echo "[4/5] Google Chrome 已安装"
fi

# 5. 配置环境变量
echo "[5/5] 配置环境变量..."
if ! grep -q "export DISPLAY=:0" ~/.bashrc; then
    echo "export DISPLAY=:0" >> ~/.bashrc
    echo "  已添加 DISPLAY=:0 到 ~/.bashrc"
fi

# 生成 Chrome 调试启动脚本
cat > ~/start_chrome_debug.sh << 'EOF'
#!/bin/bash
# 启动 Chrome 并开启远程调试端口
google-chrome --no-sandbox --remote-debugging-port=9222 --user-data-dir=~/.chrome-debug &
echo "Chrome 已启动，调试端口: 9222"
EOF
chmod +x ~/start_chrome_debug.sh

echo ""
echo "=== 配置完成 ==="
echo ""
echo "使用方法："
echo "1. 启动 Chrome 调试模式: ~/start_chrome_debug.sh"
echo "2. 测试 OpenCLI: opencli bilibili search \"AI 编程\" --sort=latest"
echo ""
echo "注意: 首次使用需要手动登录目标网站完成验证"
