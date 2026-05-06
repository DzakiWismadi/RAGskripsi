import json

# Read the enriched controls
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    controls = json.load(f)

# A.8.28: Secure coding
enrichment = {
    "keywords_en": [
        "secure coding practices",
        "secure development lifecycle",
        "code security standards",
        "secure programming",
        "application security",
        "secure code review",
        "developer security training"
    ],
    "keywords_id": [
        "praktik pengkodean aman",
        "siklus pengembangan aman",
        "standar keamanan kode",
        "pemrograman aman",
        "keamanan aplikasi",
        "tinjauan kode aman",
        "pelatihan keamanan pengembang"
    ],
    "audit_indicators_en": [
        "no secure coding standards defined",
        "developers not trained in secure coding",
        "code reviews do not include security checks",
        "vulnerabilities found in deployed code",
        "no secure coding guidelines",
        "lack of static code analysis",
        "security vulnerabilities in source code"
    ],
    "audit_indicators_id": [
        "tidak ada standar pengkodean aman",
        "pengembang tidak dilatih pengkodean aman",
        "tinjauan kode tidak termasuk pemeriksaan keamanan",
        "kerentanan ditemukan dalam kode yang digunakan",
        "tidak ada panduan pengkodean aman",
        "kurangnya analisis kode statis",
        "kerentanan keamanan dalam kode sumber"
    ],
    "related_assets_en": [
        "source code repositories",
        "development environments",
        "version control systems",
        "IDEs and code editors",
        "static analysis tools",
        "application source code"
    ],
    "related_assets_id": [
        "repositori kode sumber",
        "lingkungan pengembangan",
        "sistem kontrol versi",
        "IDE dan editor kode",
        "alat analisis statis",
        "kode sumber aplikasi"
    ],
    "security_principles_en": [
        "defense in depth",
        "secure by design",
        "least privilege",
        "fail securely",
        "input validation"
    ],
    "security_principles_id": [
        "pertahanan berlapis",
        "aman secara desain",
        "hak istimewa terendah",
        "gagal dengan aman",
        "validasi input"
    ]
}

# Find and update A.8.28
for control in controls:
    if control['control_id'] == 'A.8.28':
        control.update(enrichment)
        break

# Save the updated file
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(controls, f, ensure_ascii=False, indent=2)

print("Enriched 1 control (A.8.28)")
print("File saved successfully")
