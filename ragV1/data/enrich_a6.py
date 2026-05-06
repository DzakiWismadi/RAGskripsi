import json

# Read both files
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls.json', 'r', encoding='utf-8') as f:
    original = json.load(f)

with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    enriched = json.load(f)

# Define enrichments for A.6 controls (HR Security)
enrichments = {
    "A.6.1": {
        "keywords_en": ["background screening", "employment verification", "criminal record check", "pre-employment screening", "candidate vetting", "reference check", "employment eligibility", "background investigation", "personnel screening", "security clearance"],
        "keywords_id": ["penyaringan latar belakang", "verifikasi ketenagakerjaan", "pemeriksaan catatan kriminal", "penyaringan pra-ketenagakerjaan", "pemeriksaan kandidat", "cek referensi", "kelayakan kerja", "investigasi latar belakang", "penyaringan personel", "kliring keamanan"],
        "audit_indicators_en": ["no background checks performed", "inadequate pre-employment screening", "missing criminal record verification", "no employment reference checks", "background checks not compliant with regulations", "screening policy not defined", "inconsistent screening process", "no documentation of screening results"],
        "audit_indicators_id": ["tidak ada pemeriksaan latar belakang", "penyaringan pra-ketenagakerjaan tidak memadai", "verifikasi catatan kriminal tidak ada", "tidak ada cek referensi kerja", "pemeriksaan latar belakang tidak sesuai regulasi", "kebijakan penyaringan tidak didefinisikan", "proses penyaringan tidak konsisten", "tidak ada dokumentasi hasil penyaringan"],
        "related_assets_en": ["personnel files", "HR database", "employee records", "background check reports", "candidate information system", "employment contracts", "security clearance database"],
        "related_assets_id": ["file personel", "database HR", "catatan karyawan", "laporan pemeriksaan latar belakang", "sistem informasi kandidat", "kontrak kerja", "database kliring keamanan"],
        "security_principles_en": ["HR security", "personnel vetting", "access control foundation", "trust establishment", "compliance verification", "risk mitigation"],
        "security_principles_id": ["keamanan HR", "pemeriksaan personel", "fondasi kendali akses", "pembentukan kepercayaan", "verifikasi kepatuhan", "mitigasi risiko"]
    },
    "A.6.2": {
        "keywords_en": ["employment terms", "contractual obligations", "job descriptions", "security responsibilities", "employee agreements", "termination conditions", "employment contracts", "non-disclosure agreements", "security clauses", "personnel policies"],
        "keywords_id": ["syarat ketenagakerjaan", "kewajiban kontraktual", "deskripsi pekerjaan", "tanggung jawab keamanan", "perjanjian karyawan", "kondisi pemutusan hubungan kerja", "kontrak ketenagakerjaan", "perjanjian non-disclosure", "klausul keamanan", "kebijakan personel"],
        "audit_indicators_en": ["no employment contracts", "security responsibilities not defined", "missing NDAs", "no job descriptions", "employment terms not communicated", "no security clauses in contracts", "outdated employment agreements", "no acknowledgment of security policies"],
        "audit_indicators_id": ["tidak ada kontrak kerja", "tanggung jawab keamanan tidak didefinisikan", "NDA tidak ada", "tidak ada deskripsi pekerjaan", "syarat ketenagakerjaan tidak dikomunikasikan", "tidak ada klausul keamanan dalam kontrak", "perjanjian kerja usang", "tidak ada pengakuan kebijakan keamanan"],
        "related_assets_en": ["employment contracts", "employee handbook", "job descriptions", "HR policies", "personnel files", "security policy acknowledgments", "NDAs"],
        "related_assets_id": ["kontrak kerja", "buku pegawai", "deskripsi pekerjaan", "kebijakan HR", "file personel", "pengakuan kebijakan keamanan", "NDA"],
        "security_principles_en": ["contractual security", "responsibility assignment", "policy acknowledgment", "legal compliance", "personnel management", "security awareness foundation"],
        "security_principles_id": ["keamanan kontraktual", "penugasan tanggung jawab", "pengakuan kebijakan", "kepatuhan hukum", "manajemen personel", "fondasi kesadaran keamanan"]
    },
    "A.6.3": {
        "keywords_en": ["security awareness", "security training", "security education", "employee training", "information security awareness", "security awareness program", "mandatory training", "security consciousness", "training records", "learning management"],
        "keywords_id": ["kesadaran keamanan", "pelatihan keamanan", "pendidikan keamanan", "pelatihan karyawan", "kesadaran keamanan informasi", "program kesadaran keamanan", "pelatihan wajib", "kesadaran keamanan", "catatan pelatihan", "manajemen pembelajaran"],
        "audit_indicators_en": ["no security awareness training", "training not documented", "employees not trained on security policies", "no training schedule", "lack of security awareness", "training not updated", "no training effectiveness measurement", "new hires not trained"],
        "audit_indicators_id": ["tidak ada pelatihan kesadaran keamanan", "pelatihan tidak didokumentasikan", "karyawan tidak dilatih tentang kebijakan keamanan", "tidak ada jadwal pelatihan", "kurangnya kesadaran keamanan", "pelatihan tidak diperbarui", "tidak ada pengukuran efektivitas pelatihan", "karyawan baru tidak dilatih"],
        "related_assets_en": ["training materials", "learning management system", "training records", "security awareness content", "e-learning platform", "training certificates", "presentation materials"],
        "related_assets_id": ["materi pelatihan", "sistem manajemen pembelajaran", "catatan pelatihan", "konten kesadaran keamanan", "platform e-learning", "sertifikat pelatihan", "materi presentasi"],
        "security_principles_en": ["security culture", "human firewall", "awareness building", "knowledge transfer", "behavioral change", "security mindset"],
        "security_principles_id": ["budaya keamanan", "manusia sebagai firewall", "membangun kesadaran", "transfer pengetahuan", "perubahan perilaku", "mindset keamanan"]
    },
    "A.6.4": {
        "keywords_en": ["disciplinary process", "security violations", "employee discipline", "disciplinary actions", "security incident discipline", "formal disciplinary procedure", "sanctions for violations", "enforcement of policies", "disciplinary measures"],
        "keywords_id": ["proses disipliner", "pelanggaran keamanan", "disiplin karyawan", "tindakan disipliner", "disiplin insiden keamanan", "prosedur disipliner formal", "sanksi pelanggaran", "penegakan kebijakan", "langkah disipliner"],
        "audit_indicators_en": ["no disciplinary procedure", "security violations not addressed", "inconsistent disciplinary actions", "no documentation of disciplinary measures", "employees not aware of consequences", "disciplinary process not followed", "no escalation process", "lack of enforcement"],
        "audit_indicators_id": ["tidak ada prosedur disipliner", "pelanggaran keamanan tidak ditangani", "tindakan disipliner tidak konsisten", "tidak ada dokumentasi tindakan disipliner", "karyawan tidak sadar akan konsekuensi", "proses disipliner tidak diikuti", "tidak ada proses eskalasi", "kurangnya penegakan"],
        "related_assets_en": ["disciplinary policy", "employee handbook", "incident reports", "disciplinary records", "HR documentation system", "violation tracking system"],
        "related_assets_id": ["kebijakan disipliner", "buku pegawai", "laporan insiden", "catatan disipliner", "sistem dokumentasi HR", "sistem pelacakan pelanggaran"],
        "security_principles_en": ["accountability", "policy enforcement", "deterrence", "compliance monitoring", "consequence management", "rule of law"],
        "security_principles_id": ["akuntabilitas", "penegakan kebijakan", "pencegahan", "pemantauan kepatuhan", "manajemen konsekuensi", "supremasi hukum"]
    },
    "A.6.5": {
        "keywords_en": ["termination procedures", "offboarding", "exit process", "access revocation", "employment termination", "return of assets", "post-employment obligations", "departure procedures", "handover process"],
        "keywords_id": ["prosedur pemutusan hubungan kerja", "offboarding", "proses keluar", "pencabutan akses", "pemutusan hubungan kerja", "pengembalian aset", "kewajiban pasca-kerja", "prosedur keberangkatan", "proses serah terima"],
        "audit_indicators_en": ["no offboarding process", "access not revoked after termination", "assets not returned", "no exit interview", "accounts still active", "no documentation of termination", "keys not collected", "email not disabled"],
        "audit_indicators_id": ["tidak ada proses offboarding", "akses tidak dicabut setelah pemutusan hubungan kerja", "aset tidak dikembalikan", "tidak ada wawancara keluar", "akun masih aktif", "tidak ada dokumentasi pemutusan hubungan kerja", "kunci tidak dikumpulkan", "email tidak dinonaktifkan"],
        "related_assets_en": ["user accounts", "access cards", "company equipment", "email accounts", "building keys", "mobile devices", "company data"],
        "related_assets_id": ["akun pengguna", "kartu akses", "peralatan perusahaan", "akun email", "kunci gedung", "perangkat mobile", "data perusahaan"],
        "security_principles_en": ["access revocation", "asset protection", "separation of duties", "termination security", "post-employment confidentiality", "offboarding security"],
        "security_principles_id": ["pencabutan akses", "perlindungan aset", "pemisahan tugas", "keamanan pemutusan hubungan kerja", "kerahasiaan pasca-kerja", "keamanan offboarding"]
    },
    "A.6.6": {
        "keywords_en": ["non-disclosure agreement", "confidentiality agreement", "NDA", "secrecy agreement", "information confidentiality", "confidentiality clauses", "trade secret protection", "confidentiality obligations", "post-employment confidentiality"],
        "keywords_id": ["perjanjian non-disclosure", "perjanjian kerahasiaan", "NDA", "perjanjian kerahasiaan", "kerahasiaan informasi", "klausul kerahasiaan", "perlindungan rahasia dagang", "kewajiban kerahasiaan", "kerahasiaan pasca-kerja"],
        "audit_indicators_en": ["no NDAs signed", "confidentiality agreements missing", "NDAs not legally binding", "expired confidentiality agreements", "no NDA for contractors", "trade secrets not protected", "confidentiality obligations not defined"],
        "audit_indicators_id": ["tidak ada NDA yang ditandatangani", "perjanjian kerahasiaan tidak ada", "NDA tidak mengikat secara hukum", "perjanjian kerahasiaan kedaluwarsa", "tidak ada NDA untuk kontraktor", "rahasia dagang tidak dilindungi", "kewajiban kerahasiaan tidak didefinisikan"],
        "related_assets_en": ["NDA documents", "contract templates", "confidentiality agreements", "legal contracts", "personnel files"],
        "related_assets_id": ["dokumen NDA", "template kontrak", "perjanjian kerahasiaan", "kontrak hukum", "file personel"],
        "security_principles_en": ["confidentiality", "legal protection", "information classification", "contractual obligation", "trade secret protection", "intellectual property protection"],
        "security_principles_id": ["kerahasiaan", "perlindungan hukum", "klasifikasi informasi", "kewajiban kontraktual", "perlindungan rahasia dagang", "perlindungan kekayaan intelektual"]
    },
    "A.6.7": {
        "keywords_en": ["remote work", "teleworking", "work from home", "remote access security", "home office security", "remote work policy", "telecommuting", "mobile workforce", "remote work guidelines"],
        "keywords_id": ["kerja jarak jauh", "teleworking", "kerja dari rumah", "keamanan akses jarak jauh", "keamanan kantor rumahan", "kebijakan kerja jarak jauh", "telecommuting", "tenaga kerja mobile", "pedoman kerja jarak jauh"],
        "audit_indicators_en": ["no remote work security policy", "unsecured home networks", "personal devices used without controls", "no remote access security", "data exposed during remote work", "no physical security for home office", "unencrypted remote communications"],
        "audit_indicators_id": ["tidak ada kebijakan keamanan kerja jarak jauh", "jaringan rumahan tidak aman", "perangkat pribadi digunakan tanpa kontrol", "tidak ada keamanan akses jarak jauh", "data terekspos selama kerja jarak jauh", "tidak ada keamanan fisik untuk kantor rumahan", "komunikasi jarak jauh tidak terenkripsi"],
        "related_assets_en": ["VPN", "laptops", "mobile devices", "home network", "remote desktop", "cloud services", "collaboration tools"],
        "related_assets_id": ["VPN", "laptop", "perangkat mobile", "jaringan rumahan", "desktop jarak jauh", "layanan cloud", "alat kolaborasi"],
        "security_principles_en": ["remote access security", "endpoint protection", "network security", "data protection", "secure communication", "workplace flexibility"],
        "security_principles_id": ["keamanan akses jarak jauh", "perlindungan endpoint", "keamanan jaringan", "perlindungan data", "komunikasi aman", "fleksibilitas tempat kerja"]
    },
    "A.6.8": {
        "keywords_en": ["security incident reporting", "incident reporting channels", "whistleblowing", "security event reporting", "incident notification", "reporting procedures", "security hotline", "anonymous reporting", "escalation procedures"],
        "keywords_id": ["pelaporan insiden keamanan", "saluran pelaporan insiden", "whistleblowing", "pelaporan peristiwa keamanan", "notifikasi insiden", "prosedur pelaporan", "hotline keamanan", "pelaporan anonim", "prosedur eskalasi"],
        "audit_indicators_en": ["no incident reporting mechanism", "employees unaware of reporting channels", "underreporting of incidents", "no anonymous reporting option", "reporting process unclear", "no incident tracking system", "fear of retaliation for reporting"],
        "audit_indicators_id": ["tidak ada mekanisme pelaporan insiden", "karyawan tidak sadar akan saluran pelaporan", "pelaporan insiden kurang", "tidak ada opsi pelaporan anonim", "proses pelaporan tidak jelas", "tidak ada sistem pelacakan insiden", "takut pembalasan untuk pelaporan"],
        "related_assets_en": ["incident reporting system", "helpdesk", "security hotline", "reporting forms", "incident management platform", "communication channels"],
        "related_assets_id": ["sistem pelaporan insiden", "helpdesk", "hotline keamanan", "formulir pelaporan", "platform manajemen insiden", "saluran komunikasi"],
        "security_principles_en": ["incident response", "reporting culture", "transparency", "early detection", "security monitoring", "accountability"],
        "security_principles_id": ["respons insiden", "budaya pelaporan", "transparansi", "deteksi dini", "pemantauan keamanan", "akuntabilitas"]
    }
}

# Apply enrichments
for control in enriched:
    if control['control_id'] in enrichments:
        enrich_data = enrichments[control['control_id']]
        control['keywords_en'] = enrich_data['keywords_en']
        control['keywords_id'] = enrich_data['keywords_id']
        control['audit_indicators_en'] = enrich_data['audit_indicators_en']
        control['audit_indicators_id'] = enrich_data['audit_indicators_id']
        control['related_assets_en'] = enrich_data['related_assets_en']
        control['related_assets_id'] = enrich_data['related_assets_id']
        control['security_principles_en'] = enrich_data['security_principles_en']
        control['security_principles_id'] = enrich_data['security_principles_id']

# Save updated file
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(enriched, f, indent=2, ensure_ascii=False)

print(f"Enriched 8 A.6 controls")
print("File saved successfully")
