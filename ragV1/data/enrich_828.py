import json

# Load the enriched controls
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    controls = json.load(f)

# Find and enrich A.8.28
for control in controls:
    if control['control_id'] == 'A.8.28':
        control['keywords_en'] = ['secure coding', 'code quality', 'static analysis', 'secure development lifecycle', 'code review', 'coding standards', 'software security', 'vulnerability scanning', 'dynamic analysis', 'application security']
        control['keywords_id'] = ['pengkodean aman', 'kualitas kode', 'analisis statis', 'siklus pengembangan aman', 'tinjauan kode', 'standar pengkodean', 'keamanan perangkat lunak', 'pemindaian kerentanan', 'analisis dinamis', 'keamanan aplikasi']
        control['audit_indicators_en'] = ['no secure coding standards', 'code reviews not performed', 'static analysis not conducted', 'vulnerabilities in production code', 'lack of secure coding training', 'no code quality metrics', 'unvalidated user inputs', 'hardcoded credentials']
        control['audit_indicators_id'] = ['tidak ada standar pengkodean aman', 'tinjauan kode tidak dilakukan', 'analisis statis tidak dilakukan', 'kerentanan di kode produksi', 'tidak ada pelatihan pengkodean aman', 'tidak ada metrik kualitas kode', 'input pengguna tidak divalidasi', 'kredensial hard-coded']
        control['related_assets_en'] = ['source code repositories', 'development tools', 'IDEs', 'code analysis tools', 'version control systems', 'build servers', 'application servers']
        control['related_assets_id'] = ['repositori kode sumber', 'alat pengembangan', 'IDE', 'alat analisis kode', 'sistem kontrol versi', 'server build', 'server aplikasi']
        control['security_principles_en'] = ['secure by design', 'defense in depth', 'fail securely', 'least privilege', 'input validation', 'secure defaults']
        control['security_principles_id'] = ['aman sejak awal', 'pertahanan berlapis', 'gagal dengan aman', 'hak istimewa minimum', 'validasi input', 'pengaturan default aman']
        break

# Save the updated controls
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(controls, f, ensure_ascii=False, indent=2)

print('Enriched A.8.28')
