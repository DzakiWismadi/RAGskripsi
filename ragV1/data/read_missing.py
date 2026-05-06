import json

# Read original controls
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls.json', 'r', encoding='utf-8') as f:
    original = json.load(f)

# Find controls that need enrichment
missing_ids = ['A.6.1', 'A.6.2', 'A.6.3', 'A.6.4', 'A.6.5', 'A.6.6', 'A.6.7', 'A.6.8', 
               'A.7.1', 'A.7.2', 'A.7.3', 'A.7.4', 'A.7.5', 'A.7.6', 'A.7.7', 'A.7.8', 
               'A.7.9', 'A.7.10', 'A.7.11', 'A.7.12', 'A.7.13', 'A.7.14']

for ctrl_id in missing_ids[:5]:  # Show first 5
    control = next((c for c in original if c['control_id'] == ctrl_id), None)
    if control:
        print(f"{control['control_id']}: {control['title']}")
        print(f"  Objective: {control['objective'][:100]}...")
        print(f"  Description: {control['description'][:150]}...")
        print()
