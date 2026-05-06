import json

with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    controls = json.load(f)

enrichments = {
    "A.8.30": {
        "keywords_en": ["outsourced development", "vendor security", "third-party development", "external development contracts", "development SLAs", "vendor assessment", "code escrow", "intellectual property protection"],
        "keywords_id": ["pengembangan dialihdayakan", "keamanan vendor", "pengembangan pihak ketiga", "kontrak pengembangan eksternal", "SLA pengembangan", "penilaian vendor", "penitipan kode", "perlindungan kekayaan intelektual"],
        "audit_indicators_en": ["no vendor security assessment", "outsourced development without security clauses", "no code escrow agreement", "vendor lacks security certification"],
        "audit_indicators_id": ["tidak ada penilaian keamanan vendor", "pengembangan dialihdayakan tanpa klausa keamanan", "tidak ada perjanjian penitipan kode", "vendor lacks sertifikasi keamanan"],
        "related_assets_en": ["source code repositories", "development contracts", "vendor systems", "code escrow services"],
        "related_assets_id": ["repositori kode sumber", "kontrak pengembangan", "sistem vendor", "layanan penitipan kode"],
        "security_principles_en": ["vendor risk management", "supply chain security", "contractual security", "service continuity"],
        "security_principles_id": ["manajemen risiko vendor", "keamanan rantai pasokan", "keamanan kontraktual", "kontinuitas layanan"]
    },
    "A.8.31": {
        "keywords_en": ["environment separation", "dev-test-prod separation", "environment isolation", "segregation of duties", "environment access controls", "production protection", "test data management", "environment configuration"],
        "keywords_id": ["pemisahan lingkungan", "pemisahan dev-test-prod", "isolasi lingkungan", "pemisahan tugas", "kontrol akses lingkungan", "perlindungan produksi", "manajemen data uji", "konfigurasi lingkungan"],
        "audit_indicators_en": ["no separation between development and production", "developers have production access", "test data in production", "shared environments", "no environment controls"],
        "audit_indicators_id": ["tidak ada pemisahan antara pengembangan dan produksi", "pengembang memiliki akses produksi", "data uji dalam produksi", "lingkungan bersama", "tidak ada kontrol lingkungan"],
        "related_assets_en": ["development servers", "test servers", "production servers", "environment firewalls", "access control systems"],
        "related_assets_id": ["server pengembangan", "server pengujian", "server produksi", "firewall lingkungan", "sistem kontrol akses"],
        "security_principles_en": ["segregation of environments", "least privilege", "change management", "environment isolation"],
        "security_principles_id": ["pemisahan lingkungan", "hak istimewa最小", "manajemen perubahan", "isolasi lingkungan"]
    },
    "A.8.32": {
        "keywords_en": ["change management", "change control", "change approval", "impact assessment", "change testing", "rollback procedures", "emergency changes", "change documentation"],
        "keywords_id": ["manajemen perubahan", "kontrol perubahan", "persetujuan perubahan", "penilaian dampak", "pengujian perubahan", "prosedur rollback", "perubahan darurat", "dokumentasi perubahan"],
        "audit_indicators_en": ["unauthorized changes", "no change approval process", "changes without testing", "no rollback capability", "undocumented changes"],
        "audit_indicators_id": ["perubahan tidak sah", "tidak ada proses persetujuan perubahan", "perubahan tanpa pengujian", "tidak ada kemampuan rollback", "perubahan tidak terdokumentasi"],
        "related_assets_en": ["change management systems", "production environments", "configuration management tools", "version control systems"],
        "related_assets_id": ["sistem manajemen perubahan", "lingkungan produksi", "alat manajemen konfigurasi", "sistem kontrol versi"],
        "security_principles_en": ["change control", "authorization", "testing", "rollback capability"],
        "security_principles_id": ["kontrol perubahan", "otorisasi", "pengujian", "kemampuan rollback"]
    },
    "A.8.33": {
        "keywords_en": ["test data protection", "test data anonymization", "data masking", "synthetic test data", "production data cloning", "test data governance", "sensitive data in testing", "test data lifecycle"],
        "keywords_id": ["perlindungan data uji", "anonomisasi data uji", "penyamaran data", "data uji sintetis", "kloning data produksi", "tata kelola data uji", "data sensitif dalam pengujian", "siklus hidup data uji"],
        "audit_indicators_en": ["production data used for testing", "test data not anonymized", "real PII in test environment", "no test data controls"],
        "audit_indicators_id": ["data produksi digunakan untuk pengujian", "data uji tidak dianonimkan", "PII asli di lingkungan uji", "tidak ada kontrol data uji"],
        "related_assets_en": ["test databases", "test data repositories", "data masking tools", "anonymization software"],
        "related_assets_id": ["database uji", "repositori data uji", "alat penyamaran data", "perangkat lunak anonimisasi"],
        "security_principles_en": ["data minimization", "data protection", "privacy by design", "test data governance"],
        "security_principles_id": ["minimasi data", "perlindungan data", "privasi by design", "tata kelola data uji"]
    },
    "A.8.34": {
        "keywords_en": ["audit testing", "audit impact mitigation", "audit data protection", "audit access controls", "audit log protection", "system availability during audit", "audit evidence handling", "audit coordination"],
        "keywords_id": ["pengujian audit", "mitigasi dampak audit", "perlindungan data audit", "kontrol akses audit", "perlindungan log audit", "ketersediaan sistem selama audit", "penanganan bukti audit", "koordinasi audit"],
        "audit_indicators_en": ["audit activities causing system disruption", "audit data exposed", "unauthorized audit access", "no audit coordination"],
        "audit_indicators_id": ["aktivitas audit menyebabkan gangguan sistem", "data audit terekspos", "akses audit tidak sah", "tidak ada koordinasi audit"],
        "related_assets_en": ["production systems", "audit tools", "audit logs", "test environments"],
        "related_assets_id": ["sistem produksi", "alat audit", "log audit", "lingkungan pengujian"],
        "security_principles_en": ["system availability", "data protection", "audit coordination", "minimal disruption"],
        "security_principles_id": ["ketersediaan sistem", "perlindungan data", "koordinasi audit", "gangguan minimal"]
    }
}

updated = 0
for control in controls:
    if control['control_id'] in enrichments:
        for key, value in enrichments[control['control_id']].items():
            control[key] = value
        updated += 1

with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(controls, f, indent=2, ensure_ascii=False)

print(f"Enriched {updated} controls (A.8.30 - A.8.34)")
print("File saved successfully")
