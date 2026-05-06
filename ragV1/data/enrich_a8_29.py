import json

with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    controls = json.load(f)

# A.8.29: Security testing in development and acceptance
enrichment_a8_29 = {
    "keywords_en": ["security testing", "application security testing", "penetration testing", "vulnerability assessment", "security validation", "dynamic application security testing", "static application security testing", "security requirements verification"],
    "keywords_id": ["pengujian keamanan", "pengujian keamanan aplikasi", "pengujian penetrasi", "asesmen kerentanan", "validasi keamanan", "pengujian keamanan aplikasi dinamis", "pengujian keamanan aplikasi statis", "verifikasi persyaratan keamanan"],
    "audit_indicators_en": ["no security testing performed", "security testing not documented", "vulnerabilities found in production", "no penetration testing reports", "security requirements not validated", "testing environment lacks security controls"],
    "audit_indicators_id": ["tidak ada pengujian keamanan", "pengujian keamanan tidak didokumentasikan", "kerentanan ditemukan di produksi", "tidak ada laporan pengujian penetrasi", "persyaratan keamanan tidak divalidasi", "lingkungan pengujian tidak memiliki pengendalian keamanan"],
    "related_assets_en": ["test environments", "staging servers", "penetration testing tools", "vulnerability scanners", "application security testing platforms", "test data"],
    "related_assets_id": ["lingkungan pengujian", "server staging", "alat pengujian penetrasi", " pemindai kerentanan", "platform pengujian keamanan aplikasi", "data pengujian"],
    "security_principles_en": ["security by design", "defense in depth", "secure development lifecycle", "continuous testing", "vulnerability management", "risk-based testing"],
    "security_principles_id": ["keamanan sejak awal", "pertahanan berlapis", "siklus pengembangan yang aman", "pengujian berkelanjutan", "manajemen kerentanan", "pengujian berbasis risiko"]
}

# Find and update A.8.29
for control in controls:
    if control['control_id'] == 'A.8.29':
        control.update(enrichment_a8_29)
        break

# Save
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(controls, f, indent=2, ensure_ascii=False)

print("Enriched 1 control (A.8.29)")
print("File saved successfully")
