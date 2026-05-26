#!/usr/bin/env python3
"""Check code block 14 content."""
import re

with open('/root/note/yangmaji/article/08/wechat.html', 'r') as f:
    content = f.read()

# Find all code blocks
code_blocks = re.findall(r'<span style=\"[^\"]*monospace[^\"]*\">(.*?)</span>', content, re.DOTALL)

print(f"Total code blocks: {len(code_blocks)}")
for i, block in enumerate(code_blocks):
    # Decode HTML entities for display
    decoded = block.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
    print(f"\n=== Code block {i} ({len(block)} chars) ===")
    print(decoded[:300])
    if len(decoded) > 300:
        print("...")
