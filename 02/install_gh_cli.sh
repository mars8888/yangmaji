#!/bin/bash
# Hermes 养马记 02 - GitHub gh CLI 安装脚本
# 来源: https://github.com/mars8888/yangmaji/tree/main/02

set -e

echo "正在安装 GitHub CLI (gh)..."

# 检测系统
if command -v apt-get >/dev/null 2>&1; then
    # Ubuntu / Debian / WSL
    (type -p wget >/dev/null || sudo apt-get update && sudo apt-get install -y wget) \
      && sudo mkdir -p -m 755 /etc/apt/keyrings \
      && wget -qO- https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
      && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
      && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] \
        https://cli.github.com/packages stable main" \
        | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
      && sudo apt-get update && sudo apt-get install -y gh
elif command -v brew >/dev/null 2>&1; then
    # macOS
    brew install gh
elif command -v dnf >/dev/null 2>&1; then
    # Fedora / RHEL
    sudo dnf install -y 'dnf-command(config-manager)'
    sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
    sudo dnf install -y gh
elif command -v yum >/dev/null 2>&1; then
    # CentOS
    sudo yum install -y 'yum-utils'
    sudo yum-config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
    sudo yum install -y gh
else
    echo "不支持的系统，请手动安装: https://github.com/cli/cli#installation"
    exit 1
fi

echo ""
echo "✓ GitHub CLI 安装完成！"
echo "版本: $(gh --version)"
echo ""
echo "下一步：运行 'gh auth login' 进行认证"