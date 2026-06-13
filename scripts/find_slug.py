import json, re

# Check the comprehensive JSON key format
with open("src/data/ipoComprehensiveAnalysis.json", encoding="utf-8") as f:
    d = json.load(f)

print("Total existing comprehensive keys:", len(d))
print("Sample keys (first 5):")
for k in list(d.keys())[:5]:
    print(f"  {k}")

# Find Reliance Jio in the generated TS
with open("src/data/ipoData.ts", encoding="utf-8") as f:
    ts = f.read()

# Find the id for Reliance Jio
pattern = r'company: "Reliance Jio"[^}]*?id: "(\d+)"'
m = re.search(pattern, ts)
if m:
    jio_id = m.group(1)
    expected_slug = f"reliance-jio-{jio_id}"
    print(f"\nReliance Jio id in TS: {jio_id}")
    print(f"Expected slug: {expected_slug}")
    print(f"Exists in comprehensive JSON: {expected_slug in d}")
else:
    print("\nReliance Jio not found by regex")
    idx = ts.find("Reliance Jio")
    if idx >= 0:
        print(f"Found at position {idx}")
        print(repr(ts[idx:idx+300]))
    else:
        # Try lowercase
        idx = ts.lower().find("reliance jio")
        if idx >= 0:
            print(f"Found at position {idx} (case insensitive)")
            print(repr(ts[idx:idx+300]))

# Also check what keys from comprehensive match any slug from the detail page
# The detail page uses: slugify(stock.company) + '-' + stock.id
# stock.id is just the index string
print("\n--- Checking comprehensive JSON by name ---")
for k in d:
    if "jio" in k.lower():
        print(f"Found jio key: {k}")
        break
else:
    print("No jio key in comprehensive JSON")
