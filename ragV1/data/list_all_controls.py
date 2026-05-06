import json

with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls.json', 'r', encoding='utf-8') as f:
    controls = json.load(f)

print('All Control IDs:')
for i, c in enumerate(controls):
    print(f'{i+1}. {c["control_id"]}: {c["title"]}')
