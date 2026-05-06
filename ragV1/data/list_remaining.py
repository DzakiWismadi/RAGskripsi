import json

with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls.json', 'r', encoding='utf-8') as f:
    controls = json.load(f)

remaining = ['A.8.28', 'A.8.29', 'A.8.30', 'A.8.31', 'A.8.32', 'A.8.33', 'A.8.34']

for ctrl_id in remaining:
    control = next((c for c in controls if c['control_id'] == ctrl_id), None)
    if control:
        print(f"{control['control_id']}: {control['title']}")
        print(f"  Objective: {control['objective'][:100]}...")
        print()
