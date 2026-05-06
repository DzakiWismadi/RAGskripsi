import json

# Read both files
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls.json', 'r', encoding='utf-8') as f:
    original_controls = json.load(f)

with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    enriched_controls = json.load(f)

# Find controls needing enrichment (empty fields)
controls_to_enrich = []
for control in enriched_controls:
    if 'keywords_en' in control and len(control['keywords_en']) == 0:
        original = next((c for c in original_controls if c['control_id'] == control['control_id']), None)
        if original:
            controls_to_enrich.append({
                'id': control['control_id'],
                'title': control['title'],
                'objective': control.get('objective', ''),
                'description': control.get('description', ''),
                'implementation_guidance': control.get('implementation_guidance', '')
            })

print(f"Found {len(controls_to_enrich)} controls to enrich")
print(f"Control IDs: {[c['id'] for c in controls_to_enrich]}")
