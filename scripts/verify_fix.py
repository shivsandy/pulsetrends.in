import re

with open("src/data/ipoData.ts", encoding="utf-8") as f:
    ts = f.read()

idx = ts.find("Reliance Jio")
block_start = ts.rfind("{", 0, idx)
block_end = ts.find("}", idx)
block = ts[block_start:block_end+1]

print("=== Reliance Jio block analysis ===")
if "aiAnalysis" in block:
    ai_idx = block.find("aiAnalysis")
    print(f"Found aiAnalysis at relative offset {ai_idx}")
    print(repr(block[ai_idx:ai_idx+200]))
else:
    print("NO aiAnalysis field found!")
    # Print the last 30 lines of the block
    lines = block.split("\n")
    print("Last lines of block:")
    for l in lines[-10:]:
        print(f"  {repr(l)}")

# Check aiVerdict
print("\n--- aiVerdict ---")
if "aiVerdict" in block:
    vidx = block.find("aiVerdict")
    print(repr(block[vidx:vidx+150]))

# Check aiScores
print("\n--- aiScores ---")
if "aiScores" in block:
    sidx = block.find("aiScores")
    print(repr(block[sidx:sidx+250]))

# Count IPOs with aiAnalysis
analysis_count = ts.count("aiAnalysis:")
print(f"\nTotal aiAnalysis fields: {analysis_count}")
print(f"Total entries: {ts.count('id: \"')}")

# Check entry without aiAnalysis
no_analysis = []
for m in re.finditer(r'company: "([^"]+)"', ts):
    company = m.group(1)
    entry_start = max(0, m.start() - 200)
    entry_chunk = ts[entry_start:m.end()+100]
    if "aiAnalysis" not in entry_chunk:
        no_analysis.append(company)
        if len(no_analysis) <= 5:
            print(f"\nNo aiAnalysis for: {company}")

print(f"\nTotal without aiAnalysis: {len(no_analysis)}")
if no_analysis:
    print(f"First 5: {no_analysis[:5]}")
