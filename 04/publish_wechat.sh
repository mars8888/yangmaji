#!/bin/bash
# 养马记04 - 微信公众号一键发布脚本
# 来源: https://github.com/mars8588/yangmaji/tree/main/04
# 用法: ./publish_wechat.sh article.md "文章标题"
set -e

echo "========================================="
echo "  微信公众号自动发布脚本"
echo "========================================="
echo ""

MARKDOWN_FILE="${1:?用法: $0 <article.md> [标题]}"
TITLE="${2:-$(head -1 "$MARKDOWN_FILE" | sed 's/^# *//')}"

echo "文章: $MARKDOWN_FILE"
echo "标题: $TITLE"
echo ""

# 读取凭据
CONFIG_FILE="${WECHAT_CONFIG:-$HOME/.hermes/wechat.json}"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "错误: 找不到微信配置文件 $CONFIG_FILE"
    echo "请创建 ~/.hermes/wechat.json，包含 appId 和 appSecret"
    exit 1
fi

APP_ID=$(jq -r '.appId' "$CONFIG_FILE")
APP_SECRET=$(jq -r '.appSecret' "$CONFIG_FILE")

if [ "$APP_ID" = "null" ] || [ "$APP_SECRET" = "null" ]; then
    echo "错误: 配置文件中缺少 appId 或 appSecret"
    exit 1
fi

echo "✓ 凭据已加载 (AppID: ${APP_ID:0:8}...)"

# 获取 Token（带缓存）
TOKEN_FILE="/tmp/wechat_token.json"
TOKEN=""

if [ -f "$TOKEN_FILE" ]; then
    TIMESTAMP=$(jq -r '.timestamp' "$TOKEN_FILE")
    EXPIRES=$(jq -r '.expires_in' "$TOKEN_FILE")
    NOW=$(date +%s)
    if [ $((NOW - TIMESTAMP)) -lt $((EXPIRES - 300)) ]; then
        TOKEN=$(jq -r '.access_token' "$TOKEN_FILE")
        echo "✓ 使用缓存 Token (剩余 $((EXPIRES - NOW + TIMESTAMP))秒)"
    fi
fi

if [ -z "$TOKEN" ]; then
    echo "正在获取 Access Token..."
    TOKEN_RESP=$(curl -s "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=${APP_ID}&secret=${APP_SECRET}")
    TOKEN=$(echo "$TOKEN_RESP" | jq -r '.access_token')
    EXPIRES=$(echo "$TOKEN_RESP" | jq -r '.expires_in')
    
    if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
        echo "✗ 获取 Token 失败: $TOKEN_RESP"
        exit 1
    fi
    
    jq -n --arg t "$TOKEN" --arg e "$EXPIRES" \
        '{access_token: $t, expires_in: ($e|tonumber), timestamp: now}' > "$TOKEN_FILE"
    echo "✓ 获取新 Token (有效期 ${EXPIRES}秒)"
fi

# 上传封面图
THUMB_ID=""
ARTICLE_DIR="$(dirname "$MARKDOWN_FILE")"

for COVER_PATH in "$ARTICLE_DIR/assets/cover.png" "$ARTICLE_DIR/assets/cover-04.png" "$ARTICLE_DIR/assets/cover-*.png"; do
    if [ -f "$COVER_PATH" ]; then
        echo "✓ 找到封面图: $COVER_PATH"
        UPLOAD_RESP=$(curl -s -X POST \
            "https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=${TOKEN}&type=image" \
            -F "media=@${COVER_PATH}")
        THUMB_ID=$(echo "$UPLOAD_RESP" | jq -r '.media_id')
        if [ "$THUMB_ID" = "null" ] || [ -z "$THUMB_ID" ]; then
            echo "⚠ 封面上传失败: $UPLOAD_RESP"
        else
            echo "✓ 封面上传成功: $THUMB_ID"
        fi
        break
    fi
done

if [ -z "$THUMB_ID" ]; then
    # 尝试从素材库获取已有图片
    echo "未找到封面图，尝试从素材库获取..."
    THUMB_ID=$(curl -s -X POST \
        "https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token=${TOKEN}" \
        -H "Content-Type: application/json" \
        -d '{"type":"image","offset":0,"count":1}' | jq -r '.item[0].media_id')
    
    if [ "$THUMB_ID" = "null" ] || [ -z "$THUMB_ID" ]; then
        echo "✗ 素材库无可用图片，请上传封面图"
        exit 1
    fi
    echo "✓ 使用素材库图片: $THUMB_ID"
fi

# 调用 Python 脚本进行 Markdown → HTML 转换并发布
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python3 "$SCRIPT_DIR/wechat_publisher.py" \
    --markdown "$MARKDOWN_FILE" \
    --title "$TITLE" \
    --token "$TOKEN" \
    --thumb-id "$THUMB_ID" \
    --author "金岩"

echo ""
echo "========================================="
echo "✅ 草稿已创建成功！"
echo "请前往公众号后台确认并发布："
echo "https://mp.weixin.qq.com"
echo "========================================="
