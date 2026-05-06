import json

with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Check specific controls from each annex
test_controls = ['A.6.1', 'A.6.7', 'A.7.1', 'A.7.10', 'A.8.1', 'A.8.15', 'A.8.25']

print('Sample Control Enrichment Status:')
print('=' * 60)
for ctrl_id in test_controls:
    control = next((c for c in data if c['control_id'] == ctrl_id), None)
    if control:
        field_counts = {k: len(v) if isinstance(v, list) else 0 for k, v in control.items() if k in ['keywords_en', 'keywords_id', 'audit_indicators_en', 'audit_indicators_id', 'related_assets_en', 'related_assets_id', 'security_principles_en', 'security_principles_id']}
        total = sum(field_counts.values())
        print(f'{ctrl_id}: {total} items')
        print(f'  Keywords EN: {len(control.get("keywords_en", []))}')
        print(f'  Keywords ID: {len(control.get("keywords_id", []))}')
        print(f'  Audit Indicators EN: {len(control.get("audit_indicators_en", []))}')
        print(f'  Audit Indicators ID: {len(control.get("audit_indicators_id", []))}')
        print()

# Overall statistics
empty_count = sum(1 for c in data if len(c.get('keywords_en', [])) == 0)
print(f'Total controls: {len(data)}')
print(f'Controls with enrichment: {len(data) - empty_count}')
print(f'Controls still empty: {empty_count}')

if empty_count > 0:
    empty_ids = [c['control_id'] for c in data if len(c.get('keywords_en', [])) == 0]
    print(f'Empty control IDs: {empty_ids}')
