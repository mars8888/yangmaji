#!/usr/bin/env python3
"""Debug 45166 - examine F1 content."""
with open('/root/note/yangmaji/article/08/wechat.html', 'r') as f:
    full_html = f.read()

f1_end = len(full_html) // 16
f1 = full_html[:f1_end]

print(f"F1 length: {len(f1)}")
print(f"---CONTENT START---")
print(f1)
print(f"---CONTENT END---")
