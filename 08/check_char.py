#!/usr/bin/env python3
"""Check exact character at 1152."""
with open('/root/note/yangmaji/article/08/wechat.html', 'r') as f:
    full = f.read()

# Show character at position 1152
pos = 1152
c = full[pos]
print(f"Char at {pos}: U+{ord(c):04X} = {repr(c)}")

# Show surrounding context with character codes
for i in range(max(0,pos-20), pos+20):
    c = full[i]
    code = ord(c)
    marker = " <<<" if i == pos else ""
    if code > 127 or i == pos:
        print(f"  pos {i}: U+{code:04X} = {repr(c)}{marker}")

# Let me try: does the issue happen with the original md_to_wechat conversion?
# Or is it a different problem?

# Let me check if the issue is with the link text specifically
# Find the "wechat-04" link
idx = full.find('wechat-04')
print(f"\n'wechat-04' found at position: {idx}")

# Check if there are any invisible characters in the URL
url_start = full.find('href="https://mp.weixin.qq.com/s/wechat-04"')
if url_start >= 0:
    url_segment = full[url_start:url_start+60]
    print(f"\nURL segment repr: {repr(url_segment)}")
    for i, c in enumerate(url_segment):
        if ord(c) > 127:
            print(f"  Non-ASCII at pos {i} (absolute {url_start+i}): U+{ord(c):04X} = {repr(c)}")

# Let me also check the markdown source for invisible chars
with open('/root/note/yangmaji/article/08/article.md', 'r') as f:
    md = f.read()

print(f"\nMarkdown size: {len(md)}")
for i, c in enumerate(md):
    if ord(c) > 127 and ord(c) < 256:
        print(f"  Latin-1 char at {i}: U+{ord(c):04X}")
    if c in '\u200b\u200c\u200d\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u2060\ufeff':
        print(f"  Invisible char at {i}: U+{ord(c):04X}")
