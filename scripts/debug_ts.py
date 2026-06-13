import re

with open("src/data/ipoData.ts", encoding="utf-8") as f:
    ts = f.read()

# Find first few entries to understand the pattern
# Look for "id: \"" pattern
start = ts.find('id: "')
print("First id occurrence:")
print(repr(ts[start-5:start+100]))
print()

# Find a full entry block
entry_start = ts.find("{\n")
print("First full entry:")
print(repr(ts[entry_start:entry_start+400]))
print()

# Count entries
id_count = ts.count('id: "')
print(f"Total 'id: \"' occurrences: {id_count}")

# Check structure around company/id
idx = ts.find('company: "')
print("\nFirst company entry:")
print(repr(ts[idx:idx+300]))
