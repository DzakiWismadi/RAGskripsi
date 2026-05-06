import json

with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    controls = json.load(f)

for control in controls:
    if control['control_id'] == 'A.8.33':
        control['keywords_en'] = ['test data management', 'data protection', 'data anonymization', 'test data generation', 'data masking', 'privacy protection', 'GDPR compliance', 'sensitive data handling']
        control['keywords_id'] = ['manajemen data uji', 'perlindungan data', 'anonymisasi data', 'generasi data uji', 'masking data', 'perlindungan privasi', 'kepatuhan GDPR', 'penanganan data sensitif']
        control['audit_indicators_en'] = ['production data used in testing', 'no test data protection policy', 'test data contains PII', 'unprotected test data', 'no data anonymization']
        control['audit_indicators_id'] = ['data produksi digunakan dalam pengujian', 'tidak ada kebijakan perlindungan data uji', 'data uji mengandung PII', 'data uji tidak dilindungi', 'tidak ada anonymisasi data']
        control['related_assets_en'] = ['test databases', 'test data files', 'anonymization tools', 'data masking software', 'test environments']
        control['related_assets_id'] = ['basis data uji', 'file data uji', 'alat anonymisasi', 'perangkat lunak masking data', 'lingkungan uji']
        control['security_principles_en'] = ['data minimization', 'privacy by design', 'data protection', 'confidentiality', 'compliance']
        control['security_principles_id'] = ['minimasi data', 'privasi sejak desain', 'perlindungan data', 'kerahasiaan', 'kepatuhan']
        print('Enriched A.8.33')
        break

with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(controls, f, indent=2, ensure_ascii=False)

print('File saved successfully')
