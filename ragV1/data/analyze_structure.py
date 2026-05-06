import json

with open('iso_controls.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total controls: {len(data)}')
print('Controls range:')
print(f'  First: {data[0]["control_id"]} - {data[0]["title"]}')
print(f'  Last: {data[-1]["control_id"]} - {data[-1]["title"]}')
print(f'\nControl IDs present:')
ids = [c['control_id'] for c in data]
print(f'  Sample: {ids[:20]}')
print(f'  ...')
print(f'  End: {ids[-10:]}')
print(f'\nAnnex A themes:')
themes = set()
for c in data:
    if '.' in c['control_id']:
        theme = c['control_id'].split('.')[0]
        themes.add(theme)
print(f'  {sorted(themes)}')
