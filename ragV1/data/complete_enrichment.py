import json

# Load data
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Comprehensive enrichment mappings for all 56 controls
enrichments = {
    "A.6.1": {
        "keywords_en": ["employment screening", "background verification", "pre-employment checks", "candidate vetting", "employee background check", "reference verification", "criminal record check", "employment eligibility", "security clearance verification", "personal identity verification"],
        "keywords_id": ["penyaringan ketenagakerjaan", "verifikasi latar belakang", "pemeriksaan pra-kerja", "verifikasi kandidat", "pemeriksaan latar belakang karyawan", "verifikasi referensi", "pemeriksaan catatan kriminal", "kelayakan kerja", "verifikasi izin keamanan", "verifikasi identitas pribadi"],
        "audit_indicators_en": ["no background checks performed", "inadequate employment screening", "missing verification records", "background checks not completed before hiring", "no documented screening process", "insufficient candidate verification", "employment screening policy not followed", "background check documentation incomplete"],
        "audit_indicators_id": ["tidak ada pemeriksaan latar belakang", "penyaringan ketenagakerjaan tidak memadai", "catatan verifikasi hilang", "pemeriksaan latar belakang tidak selesai sebelum perekrutan", "tidak ada prosedur penyaringan terdokumentasi", "verifikasi kandidat tidak cukup", "kebijakan penyaringan ketenagakerjaan tidak diikuti", "dokumentasi pemeriksaan latar belakang tidak lengkap"],
        "related_assets_en": ["HR records", "employee database", "personnel files", "background check reports", "identity verification systems", "employment applications", "candidate information systems"],
        "related_assets_id": ["catatan HR", "database karyawan", "file personel", "laporan pemeriksaan latar belakang", "sistem verifikasi identitas", "aplikasi kerja", "sistem informasi kandidat"],
        "security_principles_en": ["due diligence", "trust but verify", "prevention", "defense in depth", "separation of duties", "least privilege"],
        "security_principles_id": ["due diligence", "percaya tapi verifikasi", "pencegahan", "pertahanan berlapis", "pemisahan tugas", "hak istimewa minimum"]
    },
    "A.6.2": {
        "keywords_en": ["employment contracts", "job descriptions", "security responsibilities", "employee agreements", "terms of employment", "confidentiality agreements", "security clauses", "contractor agreements", "NDAs", "security awareness agreements"],
        "keywords_id": ["kontrak kerja", "deskripsi pekerjaan", "tanggung jawab keamanan", "perjanjian karyawan", "syarat ketenagakerjaan", "perjanjian kerahasiaan", "klausa keamanan", "perjanjian kontraktor", "NDA", "perjanjian kesadaran keamanan"],
        "audit_indicators_en": ["no signed employment contracts", "security responsibilities not defined", "confidentiality agreements missing", "contractor lacks security agreement", "employment terms do not address security", "no NDA on file", "security obligations not documented", "outdated employment agreements"],
        "audit_indicators_id": ["tidak ada kontrak kerja yang ditandatangani", "tanggung jawab keamanan tidak didefinisikan", "perjanjian kerahasiaan hilang", "kontraktor tidak memiliki perjanjian keamanan", "syarat kerja tidak membahas keamanan", "tidak ada NDA", "kewajiban keamanan tidak terdokumentasi", "perjanjian kerja usang"],
        "related_assets_en": ["employment contracts", "HR policy documents", "confidentiality agreements", "contractor agreements", "employee handbook", "security policy acknowledgments"],
        "related_assets_id": ["kontrak kerja", "dokumen kebijakan HR", "perjanjian kerahasiaan", "perjanjian kontraktor", "buku pegawai", "pengakuan kebijakan keamanan"],
        "security_principles_en": ["accountability", "contractual obligation", "legal compliance", "explicit consent", "documented responsibilities"],
        "security_principles_id": ["akuntabilitas", "kewajiban kontraktual", "kepatuhan hukum", "persetujuan eksplisit", "tanggung jawab terdokumentasi"]
    },
    "A.6.3": {
        "keywords_en": ["security awareness training", "security education", "employee training", "security consciousness", "security briefings", "mandatory training", "security certification programs", "continuing education", "role-based training", "security literacy"],
        "keywords_id": ["pelatihan kesadaran keamanan", "pendidikan keamanan", "pelatihan karyawan", "kesadaran keamanan", "briefing keamanan", "pelatihan wajib", "program sertifikasi keamanan", "pendidikan berkelanjutan", "pelatihan berbasis peran", "melek keamanan"],
        "audit_indicators_en": ["no security training provided", "employees lack security awareness", "training records incomplete", "no mandatory security education", "security training not up to date", "no training attendance records", "security awareness program ineffective", "employees not trained on security policies"],
        "audit_indicators_id": ["tidak ada pelatihan keamanan", "karyawan kurang kesadaran keamanan", "catatan pelatihan tidak lengkap", "tidak ada pendidikan keamanan wajib", "pelatihan keamanan tidak mutakhir", "tidak ada catatan kehadiran pelatihan", "program kesadaran keamanan tidak efektif", "karyawan tidak dilatih tentang kebijakan keamanan"],
        "related_assets_en": ["training materials", "learning management system", "training records", "security awareness content", "e-learning platforms", "training certifications"],
        "related_assets_id": ["materi pelatihan", "sistem manajemen pembelajaran", "catatan pelatihan", "konten kesadaran keamanan", "platform e-learning", "sertifikasi pelatihan"],
        "security_principles_en": ["security culture", "continuous improvement", "defense in depth", "human firewall", "awareness first"],
        "security_principles_id": ["budaya keamanan", "peningkatan berkelanjutan", "pertahanan berlapis", "manusia sebagai firewall", "kesadaran pertama"]
    },
    "A.6.4": {
        "keywords_en": ["disciplinary process", "security violation penalties", "employee discipline", "formal disciplinary action", "security policy enforcement", "disciplinary procedures", "sanction policies", "termination procedures", "code of conduct enforcement", "disciplinary records"],
        "keywords_id": ["proses disipliner", "sanksi pelanggaran keamanan", "disiplin karyawan", "tindakan disipliner formal", "penegakan kebijakan keamanan", "prosedur disipliner", "kebijakan sanksi", "prosedur pemutusan hubungan kerja", "penegakan kode etik", "catatan disipliner"],
        "audit_indicators_en": ["no disciplinary process defined", "security violations not addressed", "disciplinary action inconsistent", "no formal disciplinary procedure", "security violations not documented", "disciplinary records missing", "no escalation process for violations", "disciplinary actions not enforced"],
        "audit_indicators_id": ["tidak ada proses disipliner yang didefinisikan", "pelanggaran keamanan tidak ditangani", "tindakan disipliner tidak konsisten", "tidak ada prosedur disipliner formal", "pelanggaran keamanan tidak terdokumentasi", "catatan disipliner hilang", "tidak ada proses eskalasi untuk pelanggaran", "tindakan disipliner tidak ditegakkan"],
        "related_assets_en": ["disciplinary policy", "employee handbook", "incident reports", "disciplinary records", "HR management system", "security incident logs"],
        "related_assets_id": ["kebijakan disipliner", "buku pegawai", "laporan insiden", "catatan disipliner", "sistem manajemen HR", "log insiden keamanan"],
        "security_principles_en": ["accountability", "enforcement", "deterrence", "consistency", "due process"],
        "security_principles_id": ["akuntabilitas", "penegakan", "pencegahan", "konsistensi", "proses yang adil"]
    },
    "A.6.5": {
        "keywords_en": ["termination procedures", "offboarding process", "access revocation", "employee exit process", "return of assets", "post-employment restrictions", "departure security", "employment termination", "exit interviews", "resignation security"],
        "keywords_id": ["prosedur pemutusan hubungan kerja", "proses offboarding", "pencabutan akses", "proses keluar karyawan", "pengembalian aset", "pembatasan pasca-kerja", "keamanan saat keberangkatan", "pemutusan hubungan kerja", "wawancara keluar", "keamanan pengunduran diri"],
        "audit_indicators_en": ["access not revoked after termination", "assets not returned", "no offboarding process", "termination procedures not followed", "accounts still active after departure", "missing exit documentation", "no post-employment security measures", "terminated employee still has system access"],
        "audit_indicators_id": ["akses tidak dicabut setelah pemutusan hubungan kerja", "aset tidak dikembalikan", "tidak ada proses offboarding", "prosedur pemutusan hubungan kerja tidak diikuti", "akun masih aktif setelah keberangkatan", "dokumentasi keluar hilang", "tidak ada tindakan keamanan pasca-kerja", "karyawan yang di-PHK masih memiliki akses sistem"],
        "related_assets_en": ["access control systems", "user accounts", "physical access cards", "company assets", "IT equipment", "building access systems"],
        "related_assets_id": ["sistem kendali akses", "akun pengguna", "kartu akses fisik", "aset perusahaan", "peralatan IT", "sistem akses gedung"],
        "security_principles_en": ["least privilege", "access revocation", "timely response", "asset protection", "knowledge retention"],
        "security_principles_id": ["hak istimewa minimum", "pencabutan akses", "respons tepat waktu", "perlindungan aset", "retensi pengetahuan"]
    },
    "A.6.6": {
        "keywords_en": ["confidentiality agreements", "non-disclosure agreements", "NDAs", "post-employment confidentiality", "trade secret protection", "non-compete agreements", "intellectual property protection", "confidentiality clauses", "proprietary information protection", "exit agreements"],
        "keywords_id": ["perjanjian kerahasiaan", "perjanjian non-disclosure", "NDA", "kerahasiaan pasca-kerja", "perlindungan rahasia dagang", "perjanjian non-kompetisi", "perlindungan kekayaan intelektual", "klausa kerahasiaan", "perlindungan informasi proprieter", "perjanjian keluar"],
        "audit_indicators_en": ["no NDA signed", "confidentiality agreement expired", "missing post-employment restrictions", "no trade secret protection", "intellectual property not protected", "confidentiality terms inadequate", "no non-compete agreement", "proprietary information unprotected"],
        "audit_indicators_id": ["tidak ada NDA yang ditandatangani", "perjanjian kerahasiaan kedaluwarsa", "hilang pembatasan pasca-kerja", "tidak ada perlindungan rahasia dagang", "kekayaan intelektual tidak dilindungi", "syarat kerahasiaan tidak memadai", "tidak ada perjanjian non-kompetisi", "informasi proprieter tidak dilindungi"],
        "related_assets_en": ["NDAs", "employment contracts", "intellectual property documentation", "confidentiality policies", "proprietary information databases"],
        "related_assets_id": ["NDA", "kontrak kerja", "dokumentasi kekayaan intelektual", "kebijakan kerahasiaan", "database informasi proprieter"],
        "security_principles_en": ["confidentiality", "legal protection", "contractual obligation", "intellectual property rights", "post-employment restrictions"],
        "security_principles_id": ["kerahasiaan", "perlindungan hukum", "kewajiban kontraktual", "hak kekayaan intelektual", "pembatasan pasca-kerja"]
    },
    "A.6.7": {
        "keywords_en": ["remote work security", "teleworking security", "home office security", "remote access security", "mobile workforce security", "telecommuting security", "work from home security", "remote work policy", "distributed work security", "off-site work security"],
        "keywords_id": ["keamanan kerja jarak jauh", "keamanan teleworking", "keamanan kantor rumah", "keamanan akses jarak jauh", "keamanan tenaga kerja mobile", "keamanan telecommuting", "keamanan kerja dari rumah", "kebijakan kerja jarak jauh", "keamanan kerja terdistribusi", "keamanan kerja di luar lokasi"],
        "audit_indicators_en": ["unsecured remote work environment", "no remote work security policy", "remote devices unencrypted", "home office network insecure", "no remote work guidelines", "teleworking risks unaddressed", "remote access not secured", "mobile devices lack security controls"],
        "audit_indicators_id": ["lingkungan kerja jarak jauh tidak aman", "tidak ada kebijakan keamanan kerja jarak jauh", "perangkat jarak jauh tidak dienkripsi", "jaringan kantor rumah tidak aman", "tidak ada pedoman kerja jarak jauh", "risiko teleworking tidak ditangani", "akses jarak jauh tidak diamankan", "perangkat mobile kurang kontrol keamanan"],
        "related_assets_en": ["remote work devices", "VPN connections", "home networks", "mobile devices", "remote access systems", "teleworking equipment"],
        "related_assets_id": ["perangkat kerja jarak jauh", "koneksi VPN", "jaringan rumah", "perangkat mobile", "sistem akses jarak jauh", "peralatan teleworking"],
        "security_principles_en": ["secure remote access", "endpoint protection", "network security", "data protection", "zero trust"],
        "security_principles_id": ["akses jarak jauh aman", "perlindungan titik akhir", "keamanan jaringan", "perlindungan data", "zero trust"]
    },
    "A.6.8": {
        "keywords_en": ["incident reporting", "security incident notification", "whistleblowing policy", "security incident escalation", "incident reporting channels", "security awareness reporting", "anomaly reporting", "security violation reporting", "incident disclosure", "reporting procedures"],
        "keywords_id": ["pelaporan insiden", "notifikasi insiden keamanan", "kebijakan whistleblowing", "eskalasi insiden keamanan", "saluran pelaporan insiden", "pelaporan kesadaran keamanan", "pelaporan anomali", "pelaporan pelanggaran keamanan", "pengungkapan insiden", "prosedur pelaporan"],
        "audit_indicators_en": ["no incident reporting mechanism", "employees unaware of reporting procedures", "incident reporting channels unclear", "no whistleblower protection", "security incidents not reported", "reporting process not documented", "incident escalation procedure undefined", "fear of reporting security issues"],
        "audit_indicators_id": ["tidak ada mekanisme pelaporan insiden", "karyawan tidak mengetahui prosedur pelaporan", "saluran pelaporan insiden tidak jelas", "tidak ada perlindungan whistleblower", "insiden keamanan tidak dilaporkan", "proses pelaporan tidak terdokumentasi", "prosedur eskalasi insiden tidak didefinisikan", "takut melaporkan masalah keamanan"],
        "related_assets_en": ["incident reporting system", "hotline systems", "reporting forms", "incident management software", "communication channels"],
        "related_assets_id": ["sistem pelaporan insiden", "sistem hotline", "formulir pelaporan", "perangkat lunak manajemen insiden", "saluran komunikasi"],
        "security_principles_en": ["incident response", "transparency", "accountability", "continuous monitoring", "security culture"],
        "security_principles_id": ["respons insiden", "transparansi", "akuntabilitas", "pemantauan berkelanjutan", "budaya keamanan"]
    }
}
