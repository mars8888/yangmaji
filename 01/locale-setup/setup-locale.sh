#!/bin/bash
# 中文字符集和 locale 设置（WSL环境）

sudo locale-gen zh_CN.UTF-8
sudo update-locale LANG=zh_CN.UTF-8

sudo apt-get update
sudo apt-get install -y \
  fonts-noto-cjk \
  fonts-wqy-zenhei \
  fonts-noto-color-emoji

fc-cache -fv

echo "Locale 设置完成！当前 LANG: $LANG"
