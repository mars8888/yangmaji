#!/usr/bin/env python3
"""Convert markdown article to WeChat-compatible HTML and publish as draft."""

import re
import json
import os
import urllib.request
import urllib.error

ARTICLE_DIR = "/root/note/yangmaji/article/08"
ARTICLE_PATH = os.path.join(ARTICLE_DIR, "article.md")
HTML_PATH = os.path.join(ARTICLE_DIR, "wechat.html")
WECHAT_CRED = "/root/.hermes/wechat.json"


def get_access_token():
    """获取 access_token"""
    with open(WECHAT_CRED, 'r') as f:
        cred = json.load(f)
    url = (
        f"https://api.weixin.qq.com/cgi-bin/token"
        f"?grant_type=client_credential"
        f"&appid={cred['appId']}"
        f"&secret={cred['appSecret']}"
    )
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read())
    return data['access_token']


def get_cover_media_id(token):
    """从素材库获取封面图 media_id"""
    url = f"https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={token}"
    payload = json.dumps({"type": "image", "offset": 0, "count": 1}, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    items = data.get("item", [])
    if items:
        return items[0]["media_id"]
    return None


def remove_emoji(text):
    """移除所有 Emoji 字符（防 45166 错误）"""
    return re.sub(
        '[\U00010000-\U0010ffff]',
        '',
        text
    )


def md_to_wechat_html(md_text):
    """将 Markdown 转换为微信公众号兼容的 HTML"""
    # 1. 移除所有图片引用 ![alt](path)
    md_text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', md_text)

    # 2. 移除 Emoji
    md_text = remove_emoji(md_text)

    # 3. 保护已有的自定义 div HTML 块为占位符
    html_blocks = []

    def protect_html_block(match):
        html_blocks.append(match.group(0))
        return f"\n__HTML_BLOCK_{len(html_blocks) - 1}__\n"

    md_text = re.sub(r'(<div.*?</div>)', protect_html_block, md_text, flags=re.DOTALL)

    lines = md_text.split('\n')
    html_lines = []
    in_code_block = False
    code_lines = []
    code_lang = ""
    in_table = False
    table_rows = []
    in_blockquote = False
    blockquote_lines = []

    def flush_code_block():
        nonlocal code_lines, code_lang
        if code_lines:
            code_content = '\n'.join(code_lines)
            # 转义 HTML
            code_content = code_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            lang_label = f"{code_lang}" if code_lang else ""
            card = (
                f'<div style="background:#1e293b;border-radius:8px;margin:15px 0;overflow:hidden;">'
                f'<div style="background:#0f172a;padding:8px 16px;font-size:12px;color:#64748b;">{lang_label}</div>'
                f'<div style="padding:16px;overflow-x:auto;">'
                f'<span style="font-family:monospace;font-size:14px;color:#34d399;line-height:1.8;white-space:pre;">{code_content}</span>'
                f'</div>'
                f'</div>'
            )
            html_lines.append(card)
        code_lines = []
        code_lang = ""

    def flush_blockquote():
        nonlocal blockquote_lines
        if blockquote_lines:
            bq_text = '\n'.join(blockquote_lines)
            card = (
                f'<div style="border-left:4px solid #22c55e;background:#f0fdf4;padding:12px 16px;'
                f'margin:15px 0;border-radius:0 8px 8px 0;">'
                f'<p style="margin:0;color:#166534;font-size:15px;line-height:1.8;">{bq_text}</p>'
                f'</div>'
            )
            html_lines.append(card)
        blockquote_lines = []

    def process_inline(text):
        """处理行内 Markdown：粗体、链接等"""
        # 行内代码 `code` - MUST be first to protect from bold/italic
        code_spans = []
        def protect_code(match):
            code_spans.append(match.group(1))
            return f"__INLINE_CODE_{len(code_spans) - 1}__"
        text = re.sub(r'`([^`]+)`', protect_code, text)

        # 粗体 **text** → <strong>
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong style="font-weight:bold;">\1</strong>', text)
        # 斜体 *text* → <em>
        text = re.sub(r'\*(.+?)\*', r'<em style="font-style:italic;">\1</em>', text)

        # 恢复行内代码
        for i, code in enumerate(code_spans):
            # Escape HTML in code
            code_escaped = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            text = text.replace(f'__INLINE_CODE_{i}__',
                f'<span style="background:#f1f5f9;padding:2px 6px;border-radius:4px;font-size:13px;color:#e11d48;font-family:monospace;">{code_escaped}</span>')

        # 链接 [text](url)
        text = re.sub(
            r'\[([^\]]+)\]\(([^)]+)\)',
            r'<a href="\2" style="color:#3b82f6;text-decoration:none;">\1</a>',
            text
        )
        return text

    def flush_table():
        nonlocal table_rows
        if len(table_rows) < 2:
            for row in table_rows:
                html_lines.append(f'<p style="margin-bottom:15px;line-height:1.8;font-size:15px;">{row}</p>')
            table_rows = []
            return

        header = table_rows[0]
        separator = table_rows[1] if len(table_rows) > 1 else ""
        body_rows = table_rows[2:]

        # 解析表头
        def parse_row(line):
            cells = line.strip().strip('|').split('|')
            return [c.strip() for c in cells]

        headers = parse_row(header)
        if len(body_rows) == 0:
            table_rows = []
            return

        th_cells = ''.join(
            f'<th style="padding:12px 10px;border:1px solid #e5e7eb;text-align:center;color:#fff;font-weight:bold;background:#3b82f6;">{h}</th>'
            for h in headers
        )

        td_rows = ''
        for row_line in body_rows:
            cells = parse_row(row_line)
            td_cells = ''.join(
                f'<td style="padding:10px;border:1px solid #e5e7eb;text-align:center;background:#fff;">{c}</td>'
                for c in cells
            )
            td_rows += f'<tr>{td_cells}</tr>'

        table_html = (
            f'<div style="overflow-x:auto;margin:15px 0;">'
            f'<table style="width:100%;border-collapse:collapse;font-size:14px;">'
            f'<thead><tr>{th_cells}</tr></thead>'
            f'<tbody>{td_rows}</tbody>'
            f'</table>'
            f'</div>'
        )
        html_lines.append(table_html)
        table_rows = []

    def parse_paragraph_text(line):
        """解析段落文本中的 Markdown 元素"""
        text = process_inline(line)
        return text

    i = 0
    while i < len(lines):
        line = lines[i]

        # 恢复 HTML 占位符
        placeholder_match = re.match(r'^__HTML_BLOCK_(\d+)__$', line.strip())
        if placeholder_match:
            idx = int(placeholder_match.group(1))
            html_lines.append(html_blocks[idx])
            i += 1
            continue

        # 代码块
        code_match = re.match(r'^```(\w*)', line)
        if code_match:
            if not in_code_block:
                flush_blockquote()
                flush_table()
                in_code_block = True
                code_lang = code_match.group(1)
                i += 1
                continue
            else:
                flush_code_block()
                in_code_block = False
                i += 1
                continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # 表格
        if re.match(r'^\|', line):
            flush_blockquote()
            in_table = True
            table_rows.append(line)
            i += 1
            continue
        elif in_table:
            flush_table()
            in_table = False

        # 块引用
        if line.startswith('>'):
            flush_code_block()
            in_blockquote = True
            bq_text = line.lstrip('>').strip()
            bq_text = process_inline(bq_text)
            blockquote_lines.append(bq_text)
            i += 1
            continue
        elif in_blockquote:
            flush_blockquote()
            in_blockquote = False

        # 标题
        h_match = re.match(r'^(#{1,3})\s+(.+)$', line)
        if h_match:
            level = len(h_match.group(1))
            text = process_inline(h_match.group(2))
            if level == 1:
                html_lines.append(f'<h1 style="font-size:22px;font-weight:bold;color:#1a1a1a;margin:25px 0 15px;line-height:1.4;border-bottom:2px solid #3b82f6;padding-bottom:8px;">{text}</h1>')
            elif level == 2:
                html_lines.append(f'<h2 style="font-size:18px;font-weight:bold;color:#1a1a1a;margin:20px 0 12px;line-height:1.4;border-left:4px solid #3b82f6;padding-left:10px;">{text}</h2>')
            else:
                html_lines.append(f'<h3 style="font-size:16px;font-weight:bold;color:#1a1a1a;margin:18px 0 10px;line-height:1.4;">{text}</h3>')
            i += 1
            continue

        # 空行
        if line.strip() == '':
            i += 1
            continue

        # 分隔线 ---
        if re.match(r'^-{3,}$', line.strip()):
            html_lines.append('<hr style="border:none;border-top:2px solid #e2e8f0;margin:20px 0;" />')
            i += 1
            continue

        # 普通文本
        text = parse_paragraph_text(line)
        if text:
            html_lines.append(f'<p style="margin-bottom:15px;line-height:1.8;font-size:15px;color:#333;">{text}</p>')

        i += 1

    # 刷新剩余内容
    if in_code_block:
        flush_code_block()
    if in_table:
        flush_table()
    if in_blockquote:
        flush_blockquote()

    return '\n'.join(html_lines)


def create_draft(token, title, content, thumb_media_id):
    """创建公众号草稿"""
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
    payload = {
        "articles": [{
            "title": title,
            "author": "金岩",
            "content": content,
            "thumb_media_id": thumb_media_id,
            "need_open_comment": 1,
            "only_fans_can_comment": 0
        }]
    }
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def main():
    # 1. 读取 Markdown
    with open(ARTICLE_PATH, 'r', encoding='utf-8') as f:
        md_text = f.read()

    print("✅ Markdown 读取成功")

    # 2. 提取标题
    title_match = re.search(r'# \[养马记\d+\]\s*(.+)', md_text)
    title = title_match.group(1).strip() if title_match else "养马记08"
    print(f"📝 标题: {title}")

    # 3. 转换为 HTML
    html_body = md_to_wechat_html(md_text)

    # 包裹完整 HTML
    html_full = f'<section style="margin:0;padding:0;font-family:-apple-system,Helvetica Neue,Helvetica,Arial,sans-serif;">{html_body}</section>'

    # 保存
    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(html_full)
    print(f"✅ HTML 已保存: {HTML_PATH}")

    # 4. 获取 token
    token = get_access_token()
    print(f"✅ access_token 获取成功")

    # 5. 获取封面 media_id
    thumb_id = get_cover_media_id(token)
    if not thumb_id:
        print("❌ 未找到封面图素材")
        return
    print(f"✅ 封面 media_id: {thumb_id}")

    # 6. 创建草稿
    try:
        result = create_draft(token, title, html_full, thumb_id)
        if "media_id" in result:
            print(f"✅ 草稿创建成功! media_id: {result['media_id']}")
        else:
            print(f"❌ 草稿创建失败: {result}")
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        print(f"❌ HTTP 错误 {e.code}: {body}")
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    main()
