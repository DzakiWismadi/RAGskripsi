import json

# Read the current enriched file
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    controls = json.load(f)

# Find and enrich A.8.34
for control in controls:
    if control['control_id'] == 'A.8.34':
        control['keywords_en'] = ['audit testing security', 'system protection', 'operational system impact', 'audit data protection', 'testing safeguards', 'audit trail protection', 'system availability', 'testing isolation']
        control['keywords_id'] = ['keamanan pengujian audit', 'perlindungan sistem', 'dampak sistem operasional', 'perlindungan data audit', 'pengamanan pengujian', 'perlindungan jejak audit', 'ketersediaan sistem', 'isolasi pengujian']
        control['audit_indicators_en'] = ['audit activities impact production systems', 'no testing safeguards in place', 'audit data exposed to unauthorized access', 'production systems degraded during audit', 'no audit testing procedures', 'audit testing affects system availability', 'no isolation between test and production']
        control['audit_indicators_id'] = ['aktivitas audit memengaruhi sistem produksi', 'tidak ada pengamanan pengujian', 'data audit terekspos', 'sistem produksi menurun saat audit', 'tidak ada prosedur pengujian audit', 'pengujian audit memengaruhi ketersediaan', 'tidak ada isolasi antara pengujian dan produksi']
        control['related_assets_en'] = ['production systems', 'audit software', 'test environments', 'operational databases', 'system monitoring tools', 'audit logs', 'production data']
        control['related_assets_id'] = ['sistem produksi', 'perangkat lunak audit', 'lingkungan pengujian', 'database operasional', 'alat pemantauan sistem', 'log audit', 'data produksi']
        control['security_principles_en'] = ['availability', 'integrity', 'confidentiality', 'testing isolation', 'system protection']
        control['security_principles_id'] = ['ketersediaan', 'integritas', 'kerahasiaan', 'isolasi pengujian', 'perlindungan sistem']
        print(f"Enriched {control['control_id']}")
        break

# Save back to file
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(controls, f, indent=2, ensure_ascii=False)

print("File saved successfully - ALL CONTROLS ENRICHED!")
