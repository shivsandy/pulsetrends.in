#!/usr/bin/env python3
"""Fix unescaped double quotes inside TS string literals in newsData.ts.
A quote is the closing delimiter if followed by comma, }, newline, or end of field.
Otherwise it's an internal quote that needs escaping."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NEWS_DATA_FILE = REPO_ROOT / "src" / "data" / "newsData.ts"

content = NEWS_DATA_FILE.read_text("utf-8")
result = []
i = 0
in_string = False
escape = False
fixed = 0

while i < len(content):
    ch = content[i]
    
    if escape:
        result.append(ch)
        escape = False
        i += 1
        continue
    
    if ch == '\\':
        result.append(ch)
        escape = True
        i += 1
        continue
    
    if ch == '"':
        if in_string:
            # Look ahead to determine if this is a closing quote or internal quote
            # Skip whitespace and check what follows
            j = i + 1
            while j < len(content) and content[j] in ' \t\r\n':
                j += 1
            next_ch = content[j] if j < len(content) else ''
            
            if next_ch in ',}\n\r]' or j >= len(content):
                # This is the closing quote
                result.append(ch)
                in_string = False
            else:
                # Internal quote - need to escape it
                result.append('\\"')
                fixed += 1
        else:
            result.append(ch)
            in_string = True
        i += 1
        continue
    
    result.append(ch)
    i += 1

NEWS_DATA_FILE.write_text(''.join(result), "utf-8")
print(f"Fixed {fixed} unescaped quotes")
