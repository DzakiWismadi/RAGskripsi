import json

with open('iso_controls.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total controls: {len(data)}')
print('Last 10 controls:')
for i in range(max(0, len(data)-10), len(data)):
    c = data[i]
    print(f'{i+1}. {c["control_id"]}: {c["title"]}')
