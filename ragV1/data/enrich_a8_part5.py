import json

# Read the current enriched controls
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    controls = json.load(f)

# Enrichments for A.8.25 and A.8.26
enrichments_a8_part5 = {
    "A.8.25": {
        "keywords_en": ["secure development lifecycle", "SDLC", "secure coding practices", "application security", "development security", "secure design", "security testing", "code review", "threat modeling", "secure deployment"],
        "keywords_id": ["siklus hidup pengembangan yang aman", "SDLC", "praktik pengkodean aman", "keamanan aplikasi", "keamanan pengembangan", "desain aman", "pengujian keamanan", "tinjauan kode", "pemodelan ancaman", "penyebaran aman"],
        "audit_indicators_en": ["no secure development lifecycle", "applications developed without security considerations", "no security testing in development", "insecure coding practices", "no code review process", "vulnerabilities in production code", "no threat modeling", "insecure deployment practices"],
        "audit_indicators_id": ["tidak ada siklus hidup pengembangan yang aman", "aplikasi dikembangkan tanpa pertimbangan keamanan", "tidak ada pengujian keamanan dalam pengembangan", "praktik pengkodean tidak aman", "tidak ada proses tinjauan kode", "kerentanan dalam kode produksi", "tidak ada pemodelan ancaman", "praktik penyebaran tidak aman"],
        "related_assets_en": ["development environments", "source code repositories", "build servers", "testing frameworks", "CI/CD pipelines", "application servers", "version control systems", "code review tools"],
        "related_assets_id": ["lingkungan pengembangan", "repositori kode sumber", "server build", "kerangka kerja pengujian", "pipa CI/CD", "server aplikasi", "sistem kontrol versi", "alat tinjauan kode"],
        "security_principles_en": ["Security by Design", "Defense in Depth", "Least Privilege", "Secure Defaults", "Fail Securely"],
        "security_principles_id": ["Keamanan sejak Desain", "Pertahanan Berlapis", "Hak Istimewa Minimum", "Default Aman", "Gagal dengan Aman"]
    },
    "A.8.26": {
        "keywords_en": ["application security requirements", "security specifications", "security functional requirements", "security non-functional requirements", "security standards", "OWASP", "security compliance", "security validation", "security acceptance criteria"],
        "keywords_id": ["persyaratan keamanan aplikasi", "spesifikasi keamanan", "persyaratan fungsional keamanan", "persyaratan non-fungsional keamanan", "standar keamanan", "OWASP", "kepatuhan keamanan", "validasi keamanan", "kriteria penerimaan keamanan"],
        "audit_indicators_en": ["no security requirements defined", "security requirements not documented", "application lacks security specifications", "no security acceptance criteria", "OWASP standards not followed", "security requirements not tested"],
        "audit_indicators_id": ["tidak ada persyaratan keamanan yang didefinisikan", "persyaratan keamanan tidak didokumentasikan", "aplikasi tidak memiliki spesifikasi keamanan", "tidak ada kriteria penerimaan keamanan", "standar OWASP tidak diikuti", "persyaratan keamanan tidak diuji"],
        "related_assets_en": ["requirement documents", "application specifications", "security standards", "test plans", "acceptance criteria documents", "OWASP documentation", "security policies"],
        "related_assets_id": ["dokumen persyaratan", "spesifikasi aplikasi", "standar keamanan", "rencana pengujian", "dokumen kriteria penerimaan", "dokumentasi OWASP", "kebijakan keamanan"],
        "security_principles_en": ["Security by Design", "Requirements Engineering", "Risk Assessment", "Compliance", "Due Diligence"],
        "security_principles_id": ["Keamanan sejak Desain", "Rekayasa Persyaratan", "Penilaian Risiko", "Kepatuhan", "Kehati-hatian"]
    }
}

# Apply enrichments
count = 0
for control in controls:
    if control['control_id'] in enrichments_a8_part5:
        for key, value in enrichments_a8_part5[control['control_id']].items():
            control[key] = value
        count += 1

# Save back to file
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(controls, f, indent=2, ensure_ascii=False)

print(f"Enriched {count} A.8 controls (part 5)")
print("File saved successfully")
