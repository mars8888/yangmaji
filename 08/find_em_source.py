#!/usr/bin/env python3
"""Find the source of the <em> in code blocks."""
import re

with open('/root/note/yangmaji/article/08/article.md', 'r') as f:
    md = f.read()

# Find all code blocks in the markdown
in_code = False
code_block_num = 0
code_content = []

for line in md.split('\n'):
    if line.startswith('```'):
        if in_code:
            # End of code block
            content = '\n'.join(code_content)
            # Check for * that could be converted to <em>
            if re.search(r'\*[^*]+\*', content) or re.search(r'\* \* \*', content):
                print(f"=== Code block {code_block_num} ===")
                print(content[:200])
                print()
            code_content = []
            in_code = False
        else:
            in_code = True
            code_block_num += 1
            code_content = []
    elif in_code:
        code_content.append(line)

# Also search for the specific pattern
print("\nSearching for '0 6 *' in markdown:")
for i, line in enumerate(md.split('\n')):
    if '0 6' in line and '*' in line:
        print(f"  Line {i}: {line.strip()[:80]}")
