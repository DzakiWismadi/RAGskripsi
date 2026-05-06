import json

with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for i, control in enumerate(data):
    print(f'{i+1}. {control["control_id"]}: {control["title"]}')
