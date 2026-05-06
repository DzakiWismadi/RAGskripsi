import json

with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    controls = json.load(f)

enrichments = {
    "A.8.28": {
        "keywords_en": ["secure coding", "coding standards", "code review", "static analysis", "secure development lifecycle", "OWASP", "secure coding practices", "code quality", "vulnerability prevention", "secure programming"],
        "keywords_id": ["pengkodean aman", "standar kode", "tinjauan kode", "analisis statis", "siklus pengembangan aman", "praktik pengkodean aman", "kualitas kode", "pencegahan kerentanan", "pemrograman aman"],
        "audit_indicators_en": ["no secure coding standards", "code not reviewed for security", "vulnerabilities in production code", "no static analysis", "insecure coding practices", "OWASP violations", "buffer overflows", "SQL injection vulnerabilities"],
        "audit_indicators_id": ["tidak ada standar pengkodean aman", "kode tidak ditinjau keamanannya", "kerentanan di kode produksi", "tidak ada analisis statis", "praktik pengkodean tidak aman"],
        "related_assets_en": ["source code repositories", "development tools", "IDEs", "code analysis tools", "version control systems", "CI/CD pipelines"],
        "related_assets_id": ["repositori kode sumber", "alat pengembangan", "IDE", "alat analisis kode", "sistem kontrol versi", "pipeline CI/CD"],
        "security_principles_en": ["secure by design", "defense in depth", "least privilege", "input validation", "output encoding"],
        "security_principles_id": ["aman secara desain", "pertahanan berlapis", "hak istimewa minimal", "validasi input", "encoding output"]
    },
    "A.8.29": {
        "keywords_en": ["security testing", "penetration testing", "vulnerability assessment", "code review", "dynamic analysis", "security validation", "acceptance testing", "test coverage", "security requirements testing"],
        "keywords_id": ["pengujian keamanan", "pengujian penetrasi", "asesmen kerentanan", "tinjauan kode", "analisis dinamis", "validasi keamanan", "pengujian penerimaan", "cakupan pengujian"],
        "audit_indicators_en": ["no security testing performed", "penetration testing not conducted", "vulnerabilities not addressed", "security requirements not tested", "no security test cases", "test coverage inadequate"],
        "audit_indicators_id": ["tidak ada pengujian keamanan", "pengujian penetrasi tidak dilakukan", "kerentanan tidak ditangani", "persyaratan keamanan tidak diuji"],
        "related_assets_en": ["test environments", "testing tools", "vulnerability scanners", "penetration testing tools", "test data", "test management systems"],
        "related_assets_id": ["lingkungan pengujian", "alat pengujian", "pemindai kerentanan", "alat pengujian penetrasi", "data pengujian", "sistem manajemen pengujian"],
        "security_principles_en": ["security validation", "vulnerability management", "test-driven security", "continuous testing", "independent testing"],
        "security_principles_id": ["validasi keamanan", "manajemen kerentanan", "keamanan teruji", "pengujian berkelanjutan"]
    },
    "A.8.30": {
        "keywords_en": ["outsourced development", "vendor management", "third-party development", "offshore development", "development agreements", "security requirements", "vendor assessment", "contract security", "external development"],
        "keywords_id": ["pengembangan dialihdayakan", "manajemen vendor", "pengembangan pihak ketiga", "pengembangan luar negeri", "perjanjian pengembangan", "persyaratan keamanan", "asesmen vendor"],
        "audit_indicators_en": ["no security clauses in contracts", "vendor not assessed for security", "no security requirements specified", "outsourced code not reviewed", "vendor security practices unknown", "no service level agreements"],
        "audit_indicators_id": ["tidak ada klausa keamanan dalam kontrak", "vendor tidak dinilai keamanannya", "persyaratan keamanan tidak ditentukan", "kode dialihdayakan tidak ditinjau"],
        "related_assets_en": ["vendor systems", "third-party code", "development contracts", "service level agreements", "source code escrow", "vendor documentation"],
        "related_assets_id": ["sistem vendor", "kode pihak ketiga", "kontrak pengembangan", "perjanjian tingkat layanan", "simpanan kode sumber"],
        "security_principles_en": ["supply chain security", "due diligence", "contract security", "vendor oversight", "continuous monitoring"],
        "security_principles_id": ["keamanan rantai pasok", "due diligence", "keamanan kontrak", "pengawasan vendor"]
    }
}

for control in controls:
    if control['control_id'] in enrichments:
        enrichment = enrichments[control['control_id']]
        control['keywords_en'] = enrichment['keywords_en']
        control['keywords_id'] = enrichment['keywords_id']
        control['audit_indicators_en'] = enrichment['audit_indicators_en']
        control['audit_indicators_id'] = enrichment['audit_indicators_id']
        control['related_assets_en'] = enrichment['related_assets_en']
        control['related_assets_id'] = enrichment['related_assets_id']
        control['security_principles_en'] = enrichment['security_principles_en']
        control['security_principles_id'] = enrichment['security_principles_id']

with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(controls, f, indent=2, ensure_ascii=False)

print(f"Enriched 3 A.8 controls")
print("File saved successfully")
