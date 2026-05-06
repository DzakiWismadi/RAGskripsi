import json

with open('iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total controls enriched: {len(data)}')

# Sample first control
c = data[0]
print(f'\n=== Sample Control: {c["control_id"]} ===')
print(f'Title: {c["title"]}')
print(f'\nkeywords_en ({len(c["keywords_en"])} items):')
print(f'  {", ".join(c["keywords_en"][:5])}...')
print(f'\nkeywords_id ({len(c["keywords_id"])} items):')
print(f'  {", ".join(c["keywords_id"][:5])}...')
print(f'\naudit_indicators_en ({len(c["audit_indicators_en"])} items):')
for i, ind in enumerate(c["audit_indicators_en"][:3], 1):
    print(f'  {i}. {ind}')
print(f'\naudit_indicators_id ({len(c["audit_indicators_id"])} items):')
for i, ind in enumerate(c["audit_indicators_id"][:3], 1):
    print(f'  {i}. {ind}')
print(f'\nrelated_assets_en ({len(c["related_assets_en"])} items):')
print(f'  {", ".join(c["related_assets_en"])}')
print(f'\nrelated_assets_id ({len(c["related_assets_id"])} items):')
print(f'  {", ".join(c["related_assets_id"])}')
print(f'\nsecurity_principles_en ({len(c["security_principles_en"])} items):')
print(f'  {", ".join(c["security_principles_en"])}')
print(f'\nsecurity_principles_id ({len(c["security_principles_id"])} items):')
print(f'  {", ".join(c["security_principles_id"])}')

# Check a few more controls
print(f'\n=== Additional Samples ===')
for i in [1, 15, 30, 60, 92]:
    c = data[i]
    print(f'\n{c["control_id"]}: {c["title"]}')
    print(f'  Audit indicators: {len(c["audit_indicators_en"])} EN, {len(c["audit_indicators_id"])} ID')
