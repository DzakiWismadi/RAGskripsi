import json
import re

# Load both files
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls.json', 'r', encoding='utf-8') as f:
    original = json.load(f)

with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    enriched = json.load(f)

# Control IDs that need enrichment
needs_enrichment = ['A.6.1', 'A.6.2', 'A.6.3', 'A.6.4', 'A.6.5', 'A.6.6', 'A.6.7', 'A.6.8',
                   'A.7.1', 'A.7.2', 'A.7.3', 'A.7.4', 'A.7.5', 'A.7.6', 'A.7.7', 'A.7.8',
                   'A.7.9', 'A.7.10', 'A.7.11', 'A.7.12', 'A.7.13', 'A.7.14',
                   'A.8.1', 'A.8.2', 'A.8.3', 'A.8.4', 'A.8.5', 'A.8.6', 'A.8.7', 'A.8.8',
                   'A.8.9', 'A.8.10', 'A.8.11', 'A.8.12', 'A.8.13', 'A.8.14', 'A.8.15',
                   'A.8.16', 'A.8.17', 'A.8.18', 'A.8.19', 'A.8.20', 'A.8.21', 'A.8.22',
                   'A.8.23', 'A.8.24', 'A.8.25', 'A.8.26', 'A.8.27', 'A.8.28', 'A.8.29',
                   'A.8.30', 'A.8.31', 'A.8.32', 'A.8.33', 'A.8.34']

# Print control details for enrichment
for ctrl_id in needs_enrichment[:5]:  # Show first 5
    control = next((c for c in original if c['control_id'] == ctrl_id), None)
    if control:
        print(f"\n{'='*60}")
        print(f"Control: {control['control_id']}")
        print(f"Title: {control['title']}")
        print(f"Objective: {control['objective']}")
        print(f"Description: {control['description'][:200]}...")
        print(f"Implementation: {control['implementation_guidance'][:200]}...")
        print(f"{'='*60}\n")