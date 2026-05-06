import json

with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find remaining empty controls
remaining = [c for c in data if len(c.get('keywords_en', [])) == 0]

print(f'Remaining controls: {len(remaining)}')
for c in remaining:
    print(f"{c['control_id']}: {c['title']}")
