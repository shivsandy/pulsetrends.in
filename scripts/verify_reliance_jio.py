import re

with open("src/data/ipoData.ts", encoding="utf-8") as f:
    ts = f.read()

# Find Reliance Jio's entry by locating its closing brace
idx = ts.find('Reliance Jio')
entry_start = ts.rfind("{", 0, idx)
# Find matching closing brace
depth = 0
for i in range(entry_start, len(ts)):
    if ts[i] == "{":
        depth += 1
    elif ts[i] == "}":
        depth -= 1
        if depth == 0:
            entry = ts[entry_start:i+1]
            break

print("=== Reliance Jio - aiAnalysis ===")
if "aiAnalysis" in entry:
    m = re.search(r'aiAnalysis: "((?:[^"\\]|\\.)*)"', entry)
    if m:
        txt = m.group(1)
        print(f"Length: {len(txt)}")
        print(f"Content preview: {txt[:200]}...")
    else:
        print("aiAnalysis key present but unreadable")
        ai_idx = entry.find("aiAnalysis")
        print(repr(entry[ai_idx:ai_idx+300]))
else:
    print("MISSING!")

print("\n=== aiVerdict ===")
m = re.search(r'aiVerdict: "([^"]*)"', entry)
print(f"Verdict: {m.group(1) if m else 'MISSING'}")

print("\n=== aiScores ===")
m = re.search(r'aiScores: \{([^}]+)\}', entry)
if m:
    print(m.group(1))

print("\n=== aiRating ===")
m = re.search(r'aiRating: "([^"]*)"', entry)
print(f"Rating: {m.group(1) if m else 'MISSING'}")

print("\n=== aiRatingScore ===")
m = re.search(r'aiRatingScore: ([^,\n]+)', entry)
print(f"Score: {m.group(1) if m else 'MISSING'}")
