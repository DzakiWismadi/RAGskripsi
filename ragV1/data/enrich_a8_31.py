import json

# Read the current file
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    controls = json.load(f)

# Enrichment for A.8.31
enrichment_831 = {
    "keywords_en": ["environment separation", "development testing production", " segregation", "environment isolation", "secure development lifecycle", "environment security"],
    "keywords_id": ["pemisahan lingkungan", "pengembangan pengujian produksi", "segregasi lingkungan", "isolasi lingkungan", "siklus pengembangan aman", "keamanan lingkungan"],
    "audit_indicators_en": ["no separation between dev test and prod", "developers have production access", "test data in production", "no environment isolation", "shared credentials across environments"],
    "audit_indicators_id": ["tidak ada pemisahan antara dev test dan prod", "developer punya akses produksi", "data pengujian di produksi", "tidak ada isolasi lingkungan", "kredensial bersama lintas lingkungan"],
    "related_assets_en": ["development servers", "testing servers", "production servers", "environment configuration", "access management systems"],
    "related_assets_id": ["server pengembangan", "server pengujian", "server produksi", "konfigurasi lingkungan", "sistem manajemen akses"],
    "security_principles_en": ["segregation of duties", "least privilege", "environment isolation", "change control"],
    "security_principles_id": ["pemisahan tugas", "hak istimewa minimum", "isolasi lingkungan", "kontrol perubahan"]
}

# Update A.8.31
for control in controls:
    if control['control_id'] == 'A.8.31':
        control.update(enrichment_831)
        break

# Save the file
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(controls, f, ensure_ascii=False, indent=2)

print("Enriched A.8.31")
