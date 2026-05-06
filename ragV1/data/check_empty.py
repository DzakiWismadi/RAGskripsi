import json

with open('iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
empty_count = 0
for control in data:
    if not control.get('keywords_en') and not control.get('keywords_id'):
        empty_count += 1
        print(f'Empty: {control["control_id"]} - {control["title"]}')
        
print(f'\nTotal empty controls: {empty_count}')
