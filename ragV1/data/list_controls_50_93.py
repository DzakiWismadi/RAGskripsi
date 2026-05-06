import json

with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls.json', 'r', encoding='utf-8') as f:
    controls = json.load(f)

print('Controls 50-93:')
for i, c in enumerate(controls[49:], start=50):
    print(f'{i}. {c["control_id"]}: {c["title"]}')
