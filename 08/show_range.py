#!/usr/bin/env python3
"""Show exact problematic content."""
with open('/root/note/yangmaji/article/08/wechat.html', 'r') as f:
    full_html = f.read()

# Show range 1100-1200
print(f"Range [1100:1200]:")
print(repr(full_html[1100:1200]))
print()

# Show range 1118:1155
print(f"Range [1118:1155] ({1155-1118} chars):")
print(repr(full_html[1118:1155]))
print()

# Check each char for unusual
for i in range(1110, 1170):
    c = full_html[i]
    code = ord(c)
    if code > 127:
        print(f"  pos {i}: U+{code:04X} = {c}")
