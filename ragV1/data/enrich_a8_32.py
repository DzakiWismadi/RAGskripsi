import json

with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for control in data:
    if control['control_id'] == 'A.8.32':
        control['keywords_en'] = ['change management', 'change control', 'change approval', 'change testing', 'change documentation', 'change logging', 'rollback procedures', 'impact assessment']
        control['keywords_id'] = ['manajemen perubahan', 'kontrol perubahan', 'persetujuan perubahan', 'pengujian perubahan', 'dokumentasi perubahan', 'pencatatan perubahan', 'prosedur rollback', 'penilaian dampak']
        control['audit_indicators_en'] = ['unapproved changes made', 'no change records', 'changes not tested', 'no rollback plan', 'change not documented']
        control['audit_indicators_id'] = ['perubahan tidak disetujui', 'tidak ada catatan perubahan', 'perubahan tidak diuji', 'tidak ada rencana rollback', 'perubahan tidak didokumentasikan']
        control['related_assets_en'] = ['production systems', 'change management system', 'test environment', 'configuration database']
        control['related_assets_id'] = ['sistem produksi', 'sistem manajemen perubahan', 'lingkungan pengujian', 'database konfigurasi']
        control['security_principles_en'] = ['change control', 'availability', 'integrity', 'accountability']
        control['security_principles_id'] = ['kontrol perubahan', 'ketersediaan', 'integritas', 'akuntabilitas']
        print('Enriched A.8.32')
        break

with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
