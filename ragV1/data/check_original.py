import json

with open('iso_controls.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total controls in original: {len(data)}')
print('First 10 controls:')
for i in range(min(10, len(data))):
    c = data[i]
    print(f'  {c["control_id"]}: {c["title"]}')
    print(f'    Fields: {list(c.keys())}')
