import json

with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls.json', 'r', encoding='utf-8') as f:
    controls = json.load(f)

# Find A.6 controls
a6_controls = [c for c in controls if c['control_id'].startswith('A.6')]
print(f"Found {len(a6_controls)} A.6 controls:")
for c in a6_controls:
    print(f"{c['control_id']}: {c['title']}")
    print(f"  Obj: {c['objective'][:80]}...")
    print()
