#!/usr/bin/env python3
"""Find the exact location of <em> in code block content."""
import re

with open('/root/note/yangmaji/article/08/wechat.html', 'r') as f:
    content = f.read()

# Find the <em> that's inside a monospace span
pattern = r'<span style=\"[^\"]*monospace[^\"]*\">.*?<em.*?</em>.*?</span>'
matches = list(re.finditer(pattern, content, re.DOTALL))

for m in matches:
    print(f"Found at position {m.start()}-{m.end()}")
    print(f"Content: {m.group()[:200]}")
    print()

# Also find all occurrences of <em> in the HTML
em_positions = [(m.start(), m.end()) for m in re.finditer(r'<em', content)]
print(f"Total <em> occurrences: {len(em_positions)}")
for start, end in em_positions:
    # Show context
    ctx_start = max(0, start - 50)
    ctx_end = min(len(content), end + 100)
    print(f"\n<em> at {start}:")
    print(f"  Context: ...{content[ctx_start:ctx_end]}...")
