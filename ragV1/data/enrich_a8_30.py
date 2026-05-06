import json

# Read the current enriched file
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    controls = json.load(f)

# Find A.8.30
for control in controls:
    if control['control_id'] == 'A.8.30':
        control['keywords_en'] = ['outsourced development', 'third-party development', 'vendor security', 'contract security', 'external development', 'supply chain security', 'developer vetting', 'code review external']
        control['keywords_id'] = ['pengembangan outsourcing', 'pengembangan pihak ketiga', 'keamanan vendor', 'keamanan kontrak', 'pengembangan eksternal', 'keamanan rantai pasok', 'vetting pengembang', 'review kode eksternal']
        control['audit_indicators_en'] = ['no security clauses in outsourcing contracts', 'vendor security assessment not performed', 'no code review process for external code', 'third-party developers have production access', 'lack of service level agreements', 'no intellectual property protection']
        control['audit_indicators_id'] = ['tidak ada klausa keamanan dalam kontrak outsourcing', 'penilaian keamanan vendor tidak dilakukan', 'tidak ada proses review kode untuk kode eksternal', 'pengembang pihak ketiga memiliki akses produksi', 'kurangnya perjanjian tingkat layanan', 'tidak ada perlindungan kekayaan intelektual']
        control['related_assets_en'] = ['source code repositories', 'development contracts', 'vendor systems', 'third-party code', 'outsourcing agreements', 'service level agreements', 'IP documentation']
        control['related_assets_id'] = ['repositori kode sumber', 'kontrak pengembangan', 'sistem vendor', 'kode pihak ketiga', 'perjanjian outsourcing', 'perjanjian tingkat layanan', 'dokumentasi IP']
        control['security_principles_en'] = ['supply chain security', 'third-party risk management', 'vendor oversight', 'contractual security controls', 'intellectual property protection', 'service level management']
        control['security_principles_id'] = ['keamanan rantai pasok', 'manajemen risiko pihak ketiga', 'pengawasan vendor', 'pengendalian keamanan kontraktual', 'perlindungan kekayaan intelektual', 'manajemen tingkat layanan']
        print(f"Enriched {control['control_id']}")
        break

# Save back
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(controls, f, indent=2, ensure_ascii=False)

print("File saved successfully")
