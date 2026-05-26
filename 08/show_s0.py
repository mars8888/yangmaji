#!/usr/bin/env python3
"""Show Section 0 content."""
import re

with open('/root/note/yangmaji/article/08/wechat.html', 'r') as f:
    full = f.read()

# Remove outer section
inner = full
if full.startswith('<section'):
    inner = full[full.find('>', full.find('<section'))+1:-len('</section>')]

# Split by h2
parts = re.split(r'(<h2.*?</h2>)', inner)
section0 = ""
for part in parts:
    if part.startswith('<h2'):
        break
    section0 += part

print(f"Section 0 ({len(section0)} chars):")
print(section0)
print("\n---REPR---")
print(repr(section0))
