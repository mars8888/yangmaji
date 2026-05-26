#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号发布器 - Markdown 转 HTML 并发布到公众号草稿
养马记04 配套脚本
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.error
import os


def remove_emoji(text):
    """移除所有 Emoji 字符（防止微信 API 返回 45166 错误）"""
    # 移除常见 Emoji 范围（不包括正常中文字符）
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f900-\U0001f9FF"  # supplemental
        "\U0001fa00-\U0001fa6F"  # chess
        "\U0001fa70-\U0001faff"  # symbols extended
        "\U00002600-\U000026FF"  # misc symbols
        "\U00002300-\U000023FF"  # technical
        "]+",
        re.UNICODE
    )
    return emoji_pattern.sub('', text)


def escape_html(text):
    """转义 HTML 特殊字符"""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def code_block_to_div(match):
    """将 Markdown 代码块转为微信兼容的深色卡片"""
    lang = match.group(1) or ''
    code = match.group(2)
    # 转义 HTML 字符
    code = escape_html(code)
    lines = [l for l in code.strip().split('\n') if l]  # 移除空行
    
    if not lines:
        return ''
    
    line_html = '\n'.join(
        f'<p style="color:#34d399;font-size:15px;margin:0 0 6px;line-height:1.6;font-family:monospace;">{line}</p>'
        for line in lines
    )
    
    return f'<div style="background:#1e293b;padding:18px 20px;margin:18px 0;border-radius:10px;font-family:monospace;">\n{line_html}\n</div>'


def quote_to_div(text):
    """将多行引用块合并为一个绿色卡片"""
    # 先收集所有引用行
    lines = text.split('\n')
    result = []
    quote_buffer = []
    
    for line in lines:
        if line.strip().startswith('>'):
            quote_text = re.sub(r'^>\s*', '', line.strip())
            quote_buffer.append(quote_text)
        else:
            if quote_buffer:
                # 处理已收集的引用
                full_quote = ' '.join(quote_buffer)
                result.append(
                    f'<div style="background:#ecfdf5;padding:16px 20px;margin:20px 0;border-radius:8px;border-left:4px solid #10b981;">'
                    f'<p style="font-size:16px;line-height:1.8;color:#065f46;margin:0;">{full_quote}</p></div>'
                )
                quote_buffer = []
            result.append(line)
    
    if quote_buffer:
        full_quote = ' '.join(quote_buffer)
        result.append(
            f'<div style="background:#ecfdf5;padding:16px 20px;margin:20px 0;border-radius:8px;border-left:4px solid #10b981;">'
            f'<p style="font-size:16px;line-height:1.8;color:#065f46;margin:0;">{full_quote}</p></div>'
        )
    
    return '\n'.join(result)


def md_to_wechat_html(md_text):
    """将 Markdown 转为微信公众号兼容的 HTML"""
    # 1. 移除所有 Emoji（必须第一步做）
    md_text = remove_emoji(md_text)
    
    # 2. 移除 Markdown 图片语法 ![alt](path)
    md_text = re.sub(r'!\[.*?\]\(.*?\)', '', md_text)
    
    # 3. 保护自定义 HTML 块（<div>...</div>），替换为占位符
    html_blocks = []
    def save_html_block(match):
        html_blocks.append(match.group(0))
        return f'__HTML_BLOCK_{len(html_blocks)-1}__'
    
    md_text = re.sub(r'<div.*?</div>', save_html_block, md_text, flags=re.DOTALL)
    
    # 4. 代码块转换
    md_text = re.sub(r'```(\w*)\n(.*?)```', code_block_to_div, md_text, flags=re.DOTALL)
    
    # 5. 引用块转换
    md_text = quote_to_div(md_text)
    
    # 6. 标题转换
    md_text = re.sub(
        r'^### (.+)$',
        r'<h3 style="margin:30px 0 15px;font-size:18px;font-weight:bold;color:#333;">\1</h3>',
        md_text, flags=re.MULTILINE
    )
    md_text = re.sub(
        r'^## (.+)$',
        r'<h2 style="margin:35px 0 18px;font-size:20px;font-weight:bold;color:#333;">\1</h2>',
        md_text, flags=re.MULTILINE
    )
    md_text = re.sub(
        r'^# (.+)$',
        r'<h1 style="margin:40px 0 20px;font-size:24px;font-weight:bold;color:#333;">\1</h1>',
        md_text, flags=re.MULTILINE
    )
    
    # 7. 加粗转换
    md_text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', md_text)
    
    # 8. 斜体转换
    md_text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', md_text)
    
    # 9. 链接转换
    md_text = re.sub(
        r'\[(.+?)\]\((.+?)\)',
        r'<a href="\2" style="color:#03696e;text-decoration:underline;">\1</a>',
        md_text
    )
    
    # 10. 水平线转换
    md_text = re.sub(r'^---+$', '<hr style="margin:25px 0;border:none;border-top:1px solid #e5e7eb;" />', md_text, flags=re.MULTILINE)
    
    # 11. 段落包裹（跳过已是 HTML 的行和空行）
    lines = md_text.split('\n')
    html_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        if not stripped:
            continue
        
        # 跳过 HTML 标签行
        if stripped.startswith('<h') or stripped.startswith('<div') or \
           stripped.startswith('<p') or stripped.startswith('<strong') or \
           stripped.startswith('<a') or stripped.startswith('<em') or \
           stripped.startswith('<hr') or stripped.startswith('__HTML_BLOCK'):
            html_lines.append(stripped)
            continue
        
        # 普通文本包裹为段落
        html_lines.append(
            f'<p style="margin-bottom:15px;line-height:1.8;font-size:16px;">{stripped}</p>'
        )
    
    html = '\n'.join(html_lines)
    
    # 12. 还原 HTML 块占位符
    for i, block in enumerate(html_blocks):
        html = html.replace(f'__HTML_BLOCK_{i}__', block)
    
    # 13. 清理空段落
    html = re.sub(r'<p[^>]*>\s*</p>', '', html)
    
    return html


def create_draft(token, title, content, thumb_media_id, author="金岩"):
    """创建公众号草稿"""
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
    
    data = {
        "articles": [{
            "title": title,
            "author": author,
            "content": content,
            "thumb_media_id": thumb_media_id,
            "need_open_comment": 1,
            "only_fans_can_comment": 0
        }]
    }
    
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"}
    )
    
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"✗ HTTP 错误: {e.code}")
        print(f"  响应: {e.read().decode()}")
        sys.exit(1)
    
    if "media_id" not in result:
        errcode = result.get("errcode", "unknown")
        errmsg = result.get("errmsg", "unknown")
        print(f"✗ 创建草稿失败: errcode={errcode}, errmsg={errmsg}")
        
        if errcode == 45166:
            print("\n💡 45166 错误常见原因:")
            print("   1. 内容中包含 Emoji 字符")
            print("   2. 不闭合的 HTML 标签")
            print("   3. 非法控制字符")
            print("   建议: 先用 '<p>测试</p>' 确认 Token 和封面有效")
        
        sys.exit(1)
    
    return result["media_id"]


def main():
    parser = argparse.ArgumentParser(description="微信公众号发布器")
    parser.add_argument("--markdown", required=True, help="Markdown 文件路径")
    parser.add_argument("--title", required=True, help="文章标题")
    parser.add_argument("--token", required=True, help="微信 Access Token")
    parser.add_argument("--thumb-id", required=True, help="封面图 media_id")
    parser.add_argument("--author", default="金岩", help="作者名")
    args = parser.parse_args()
    
    # 读取 Markdown
    with open(args.markdown, "r", encoding="utf-8") as f:
        md_text = f.read()
    
    print(f"✓ 读取文章: {args.markdown} ({len(md_text)} 字符)")
    
    # 转换 HTML
    html_content = md_to_wechat_html(md_text)
    print(f"✓ 转换完成: HTML 长度 {len(html_content)} 字符")
    
    # 创建草稿
    draft_id = create_draft(
        token=args.token,
        title=args.title,
        content=html_content,
        thumb_media_id=args.thumb_id,
        author=args.author
    )
    
    print(f"✓ 草稿已创建: {draft_id}")
    print(f"  请在公众号后台检查并发布: https://mp.weixin.qq.com")
    
    # 同时保存 HTML 文件供预览
    article_dir = os.path.dirname(args.markdown)
    html_path = os.path.join(article_dir, "wechat.html")
    
    # 包装为完整 HTML 方便本地预览
    preview_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{args.title}</title>
<style>
body {{ max-width: 750px; margin: 0 auto; padding: 20px; font-family: -apple-system, sans-serif; line-height: 1.8; color: #333; }}
</style>
</head>
<body>
{html_content}
</body>
</html>"""
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(preview_html)
    
    print(f"✓ 预览文件: {html_path}")


if __name__ == "__main__":
    main()
