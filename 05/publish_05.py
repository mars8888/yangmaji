#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05 期专用转换器 - 逐行处理，避免正则问题"""

import json
import re
import sys
import urllib.request
import urllib.error
import os


def remove_emoji(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"  # dingbats
        "\U0001f900-\U0001f9FF"  # supplemental
        "\U0001fa00-\U0001fa6F"  # chess
        "\U0001fa70-\U0001faff"  # symbols extended
        "\U00002600-\U000026FF"  # misc symbols
        "\u200d"                  # zero-width joiner
        "\u20e3"                  # combining enclosing keycap
        "\ufe0f"                  # variation selector
        "\u2764"                  # heart
        "]+",
        re.UNICODE
    )
    return emoji_pattern.sub('', text)


def escape_html(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def process_inline(text):
    """处理行内元素：粗体、斜体、代码、链接"""
    # 行内代码（先处理，避免干扰其他转换）
    parts = []
    segments = re.split(r'`([^`]+)`', text)
    for i, seg in enumerate(segments):
        if i % 2 == 1:  # 代码部分
            parts.append(f'<code style="background:#f1f5f9;padding:2px 6px;border-radius:4px;font-size:15px;font-family:monospace;color:#e11d48;">{escape_html(seg)}</code>')
        else:  # 普通部分
            # 粗体
            seg = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', seg)
            # 斜体
            seg = re.sub(r'\*(.+?)\*', r'<em>\1</em>', seg)
            # 链接
            seg = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" style="color:#03696e;text-decoration:underline;">\1</a>', seg)
            parts.append(seg)
    return ''.join(parts)


def convert_table(lines):
    """转换 Markdown 表格"""
    if len(lines) < 2:
        return lines

    headers = [h.strip() for h in lines[0].strip('|').split('|') if h.strip()]
    rows = []
    for line in lines[2:]:
        cells = [c.strip() for c in line.strip('|').split('|') if c.strip()]
        if cells:
            rows.append(cells)

    if not rows:
        return lines

    html = []
    html.append('<div style="overflow-x:auto;margin:20px 0;">')
    html.append('<table style="width:100%;border-collapse:collapse;font-size:15px;">')
    html.append('<thead><tr style="background:#03696e;color:#fff;">')
    for h in headers:
        html.append(f'<th style="padding:10px 12px;text-align:left;border:1px solid #03696e;">{process_inline(escape_html(h))}</th>')
    html.append('</tr></thead>')
    html.append('<tbody>')
    for i, row in enumerate(rows):
        bg = '#f8fafc' if i % 2 == 0 else '#fff'
        html.append(f'<tr style="background:{bg};">')
        for cell in row:
            html.append(f'<td style="padding:10px 12px;border:1px solid #e2e8f0;">{process_inline(escape_html(cell))}</td>')
        html.append('</tr>')
    html.append('</tbody></table></div>')
    return html


def md_to_wechat_html(md_text):
    # 1. 移除 Emoji
    md_text = remove_emoji(md_text)
    # 2. 移除 Markdown 图片
    md_text = re.sub(r'!\[.*?\]\(.*?\)', '', md_text)
    # 3. 移除行首空格
    md_text = '\n'.join(line.lstrip() for line in md_text.split('\n'))

    lines = md_text.split('\n')
    html_parts = []

    in_code = False
    code_lines = []
    in_table = False
    table_lines = []
    in_quote = False
    quote_lines = []

    def flush_table():
        nonlocal in_table, table_lines
        if table_lines:
            table_html = convert_table(table_lines)
            html_parts.extend(table_html)
        table_lines = []
        in_table = False

    def flush_quote():
        nonlocal in_quote, quote_lines
        if quote_lines:
            text = ' '.join(quote_lines)
            html_parts.append(
                f'<div style="background:#ecfdf5;padding:16px 20px;margin:20px 0;border-radius:8px;border-left:4px solid #10b981;">'
                f'<p style="font-size:16px;line-height:1.8;color:#065f46;margin:0;">{process_inline(text)}</p></div>'
            )
        quote_lines = []
        in_quote = False

    for line in lines:
        stripped = line.strip()

        # 代码块
        if stripped.startswith('```'):
            if not in_code:
                flush_quote()
                flush_table()
                in_code = True
                code_lines = []
                continue
            else:
                # 闭合代码块
                escaped_lines = [escape_html(l) for l in code_lines if l.strip()]
                if escaped_lines:
                    html_parts.append('<div style="background:#1e293b;padding:18px 20px;margin:18px 0;border-radius:10px;font-family:monospace;">')
                    for l in escaped_lines:
                        html_parts.append(f'<p style="color:#34d399;font-size:15px;margin:0 0 6px;line-height:1.6;font-family:monospace;">{l}</p>')
                    html_parts.append('</div>')
                code_lines = []
                in_code = False
                continue

        if in_code:
            code_lines.append(stripped)
            continue

        # 空行
        if not stripped:
            flush_quote()
            flush_table()
            continue

        # 引用块
        if stripped.startswith('>'):
            flush_table()
            if not in_quote:
                in_quote = True
                quote_lines = []
            quote_lines.append(stripped.lstrip('>').lstrip())
            continue
        else:
            flush_quote()

        # 表格行
        if stripped.startswith('|'):
            if not in_table:
                flush_quote()
                in_table = True
                table_lines = []
            table_lines.append(stripped)
            continue
        else:
            flush_table()

        # 分隔线
        if re.match(r'^---+$', stripped):
            html_parts.append('<hr style="margin:25px 0;border:none;border-top:1px solid #e5e7eb;" />')
            continue

        # 标题
        m = re.match(r'^### (.+)$', stripped)
        if m:
            html_parts.append(f'<h3 style="margin:30px 0 15px;font-size:18px;font-weight:bold;color:#333;">{process_inline(m.group(1))}</h3>')
            continue

        m = re.match(r'^## (.+)$', stripped)
        if m:
            html_parts.append(f'<h2 style="margin:35px 0 18px;font-size:20px;font-weight:bold;color:#333;">{process_inline(m.group(1))}</h2>')
            continue

        m = re.match(r'^# (.+)$', stripped)
        if m:
            html_parts.append(f'<h1 style="margin:40px 0 20px;font-size:24px;font-weight:bold;color:#333;">{process_inline(m.group(1))}</h1>')
            continue

        # 列表项
        if re.match(r'^[-*] ', stripped):
            content = re.sub(r'^[-*] ', '', stripped)
            html_parts.append(
                f'<p style="margin-bottom:10px;line-height:1.8;font-size:16px;padding-left:16px;position:relative;">'
                f'<span style="color:#03696e;margin-right:8px;">●</span>{process_inline(content)}</p>'
            )
            continue

        # 普通段落
        html_parts.append(f'<p style="margin-bottom:15px;line-height:1.8;font-size:16px;">{process_inline(stripped)}</p>')

    # 清理
    flush_table()
    flush_quote()

    return '\n'.join(html_parts)


def create_draft(token, title, content, thumb_media_id, author="金岩"):
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
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=60)
    result = json.loads(resp.read())

    if "media_id" not in result:
        errcode = result.get("errcode", "unknown")
        errmsg = result.get("errmsg", "unknown")
        print(f"✗ 创建草稿失败: errcode={errcode}, errmsg={errmsg}")

        if errcode == 45166:
            # 检查标签
            import re as re2
            opens = re2.findall(r'<(?!/)(?!hr|br)([a-z]+)[^>]*[^/]>|<(?!/)(?!hr|br)([a-z]+)[^>]*/>', content)
            closings = re2.findall(r'</([a-z]+)>', content)
            print(f"   标签诊断: 开标签 {len(opens)}, 闭标签 {len(closings)}")

        sys.exit(1)

    return result["media_id"]


def main():
    markdown_path = "/root/note/yangmaji/article/05/article.md"
    title = "[养马记五] qwen-tts 语音输出：让公众号文章开口说话"

    with open(os.path.expanduser('~/.hermes/wechat.json')) as f:
        creds = json.load(f)

    # 获取 Token
    url = "https://api.weixin.qq.com/cgi-bin/stable_token"
    body = json.dumps({
        "grant_type": "client_credential",
        "appid": creds['appId'],
        "secret": creds['appSecret']
    }).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req, timeout=30)
    result = json.loads(resp.read())
    token = result['access_token']
    print(f"✓ Token 获取成功")

    # 获取封面图
    url2 = f"https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={token}"
    body2 = json.dumps({"type":"image","offset":0,"count":1}).encode()
    req2 = urllib.request.Request(url2, data=body2, headers={"Content-Type": "application/json"})
    resp2 = urllib.request.urlopen(req2, timeout=30)
    result2 = json.loads(resp2.read())
    thumb_id = result2['item'][0]['media_id']
    print(f"✓ 封面图: {thumb_id}")

    with open(markdown_path, "r", encoding="utf-8") as f:
        md_text = f.read()
    print(f"✓ 读取文章: {markdown_path} ({len(md_text)} 字符)")

    html_content = md_to_wechat_html(md_text)
    print(f"✓ 转换完成: HTML 长度 {len(html_content)} 字符")

    draft_id = create_draft(
        token=token,
        title=title,
        content=html_content,
        thumb_media_id=thumb_id,
        author="金岩"
    )

    print(f"✓ 草稿已创建: {draft_id}")
    print(f"  请在公众号后台检查并发布: https://mp.weixin.qq.com")

    article_dir = os.path.dirname(markdown_path)
    html_path = os.path.join(article_dir, "wechat.html")

    preview_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
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
