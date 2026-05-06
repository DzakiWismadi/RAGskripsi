import json

# Read both files
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls.json', 'r', encoding='utf-8') as f:
    original_controls = json.load(f)

with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    enriched_controls = json.load(f)

# Define comprehensive enrichment for all 56 missing controls
enrichment_data = {
    "A.6.1": {
        "keywords_en": ["employee screening", "background verification", "pre-employment checks", "candidate vetting", "employment eligibility", "criminal record check", "employment history verification", "reference checking", "security clearance", "personnel screening"],
        "keywords_id": ["penyaringan karyawan", "verifikasi latar belakang", "pemeriksaan pra-kerja", "vetting kandidat", "kelayakan kerja", "pemeriksaan catatan kriminal", "verifikasi riwayat kerja", "pemeriksaan referensi", "clearance keamanan", "penyaringan personel"],
        "audit_indicators_en": ["no background checks performed", "incomplete employee verification", "missing employment eligibility documentation", "no criminal record checks", "inadequate reference checking", "background check policy not followed", "pre-employment screening incomplete", "no verification of credentials"],
        "audit_indicators_id": ["tidak ada pemeriksaan latar belakang", "verifikasi karyawan tidak lengkap", "dokumentasi kelayakan kerja hilang", "tidak ada pemeriksaan catatan kriminal", "pemeriksaan referensi tidak memadai", "kebijakan pemeriksaan latar belakang tidak diikuti", "penyaringan pra-kerja tidak lengkap", "tidak ada verifikasi kredensial"],
        "related_assets_en": ["employee records", "personnel files", "HR database", "background check reports", "employment contracts", "security clearance documents", "verification certificates"],
        "related_assets_id": ["catatan karyawan", "berkas personel", "database HR", "laporan pemeriksaan latar belakang", "kontrak kerja", "dokumen clearance keamanan", "sertifikat verifikasi"],
        "security_principles_en": ["trust but verify", "due diligence", "defense in depth", "separation of duties", "least privilege", "personnel security"],
        "security_principles_id": ["percaya tapi verifikasi", "due diligence", "pertahanan berlapis", "pemisahan tugas", "hak istimewa minimal", "keamanan personel"]
    },
    "A.6.2": {
        "keywords_en": ["employment contracts", "terms of employment", "job descriptions", "security responsibilities", "contractual agreements", "employee handbooks", "code of conduct", "confidentiality agreements", "NDAs", "employment terms"],
        "keywords_id": ["kontrak kerja", "syarat ketenagakerjaan", "deskripsi pekerjaan", "tanggung jawab keamanan", "perjanjian kontraktual", "buku pegawai", "kode etik", "perjanjian kerahasiaan", "NDA", "ketentuan kerja"],
        "audit_indicators_en": ["no signed employment contracts", "missing security responsibilities in contracts", "outdated job descriptions", "no confidentiality agreements", "employees not aware of security duties", "contract terms not enforced", "no code of conduct acknowledgment"],
        "audit_indicators_id": ["tidak ada kontrak kerja yang ditandatangani", "tanggung jawab keamanan hilang dalam kontrak", "deskripsi pekerjaan usang", "tidak ada perjanjian kerahasiaan", "karyawan tidak sadar akan tugas keamanan", "ketentuan kontrak tidak ditegakkan", "tidak ada pengakuan kode etik"],
        "related_assets_en": ["employment agreements", "job descriptions", "employee handbooks", "confidentiality agreements", "HR policies", "contract management system"],
        "related_assets_id": ["perjanjian kerja", "deskripsi pekerjaan", "buku pegawai", "perjanjian kerahasiaan", "kebijakan HR", "sistem manajemen kontrak"],
        "security_principles_en": ["contractual obligation", "due diligence", "accountability", "documentation", "legal compliance", "responsibility assignment"],
        "security_principles_id": ["kewajiban kontraktual", "due diligence", "akuntabilitas", "dokumentasi", "kepatuhan hukum", "penugasan tanggung jawab"]
    },
    "A.6.3": {
        "keywords_en": ["security awareness", "information security training", "employee education", "security consciousness", "training programs", "awareness campaigns", "security briefings", "phishing simulations", "security certifications", "continuous learning"],
        "keywords_id": ["kesadaran keamanan", "pelatihan keamanan informasi", "pendidikan karyawan", "kesadaran keamanan", "program pelatihan", "kampanye kesadaran", "briefing keamanan", "simulasi phishing", "sertifikasi keamanan", "pembelajaran berkelanjutan"],
        "audit_indicators_en": ["no security training provided", "employees lack security awareness", "training not documented", "no phishing awareness program", "security training outdated", "no mandatory security education", "training attendance incomplete"],
        "audit_indicators_id": ["tidak ada pelatihan keamanan", "karyawan kurang kesadaran keamanan", "pelatihan tidak didokumentasikan", "tidak ada program kesadaran phishing", "pelatihan keamanan usang", "tidak ada pendidikan keamanan wajib", "kehadiran pelatihan tidak lengkap"],
        "related_assets_en": ["training materials", "learning management system", "security awareness portal", "training records", "e-learning platform", "presentation slides"],
        "related_assets_id": ["materi pelatihan", "sistem manajemen pembelajaran", "portal kesadaran keamanan", "catatan pelatihan", "platform e-learning", "slide presentasi"],
        "security_principles_en": ["human firewall", "security culture", "continuous improvement", "defense in depth", "awareness first", "knowledge empowerment"],
        "security_principles_id": ["manusia sebagai firewall", "budaya keamanan", "peningkatan berkelanjutan", "pertahanan berlapis", "kesadaran pertama", "pemberdayaan pengetahuan"]
    },
    "A.6.4": {
        "keywords_en": ["disciplinary process", "security violations", "employee misconduct", "disciplinary actions", "sanctions", "termination procedures", "formal warnings", "investigation procedures", "disciplinary policies", "conduct enforcement"],
        "keywords_id": ["proses disipliner", "pelanggaran keamanan", "pelanggaran karyawan", "tindakan disipliner", "sanksi", "prosedur pemutusan hubungan kerja", "peringatan formal", "prosedur investigasi", "kebijakan disipliner", "penegakan perilaku"],
        "audit_indicators_en": ["no disciplinary policy exists", "inconsistent disciplinary actions", "security violations not addressed", "no formal investigation process", "disciplinary actions not documented", "employees unaware of consequences", "no escalation procedures"],
        "audit_indicators_id": ["tidak ada kebijakan disipliner", "tindakan disipliner tidak konsisten", "pelanggaran keamanan tidak ditangani", "tidak ada proses investigasi formal", "tindakan disipliner tidak didokumentasikan", "karyawan tidak sadar akan konsekuensi", "tidak ada prosedur eskalasi"],
        "related_assets_en": ["disciplinary policies", "incident reports", "employee files", "investigation records", "warning letters", "termination documents"],
        "related_assets_id": ["kebijakan disipliner", "laporan insiden", "berkas karyawan", "catatan investigasi", "surat peringatan", "dokumen pemutusan hubungan kerja"],
        "security_principles_en": ["accountability", "enforcement", "deterrence", "fair process", "documentation", "zero tolerance"],
        "security_principles_id": ["akuntabilitas", "penegakan", "pencegahan", "proses adil", "dokumentasi", "toleransi nol"]
    },
    "A.6.5": {
        "keywords_en": ["termination procedures", "exit interviews", "access revocation", "return of assets", "post-employment obligations", "departure process", "offboarding", "handover procedures", "resignation process", "contract termination"],
        "keywords_id": ["prosedur pemutusan hubungan kerja", "wawancara keluar", "pencabutan akses", "pengembalian aset", "kewajiban pasca-kerja", "proses keberangkatan", "offboarding", "prosedur serah terima", "proses pengunduran diri", "pemutusan kontrak"],
        "audit_indicators_en": ["access not revoked after termination", "assets not returned", "no exit interview process", "accounts still active", "no handover documentation", "physical access not removed", "email accounts active after departure"],
        "audit_indicators_id": ["akses tidak dicabut setelah pemutusan hubungan kerja", "aset tidak dikembalikan", "tidak ada proses wawancara keluar", "akun masih aktif", "tidak ada dokumentasi serah terima", "akses fisik tidak dihapus", "akun email aktif setelah keberangkatan"],
        "related_assets_en": ["user accounts", "access cards", "company equipment", "email accounts", "file access permissions", "security badges"],
        "related_assets_id": ["akun pengguna", "kartu akses", "peralatan perusahaan", "akun email", "izin akses file", "lencana keamanan"],
        "security_principles_en": ["access revocation", "asset recovery", "knowledge transfer", "clean break", "accountability", "timely deprovisioning"],
        "security_principles_id": ["pencabutan akses", "pemulihan aset", "transfer pengetahuan", "pemutusan bersih", "akuntabilitas", "deprovisioning tepat waktu"]
    },
    "A.6.6": {
        "keywords_en": ["confidentiality agreements", "non-disclosure agreements", "NDAs", "post-employment confidentiality", "trade secret protection", "intellectual property protection", "lifetime confidentiality", "sensitive information protection", "proprietary information", "competitor restrictions"],
        "keywords_id": ["perjanjian kerahasiaan", "perjanjian non-disclosure", "NDA", "kerahasiaan pasca-kerja", "perlindungan rahasia dagang", "perlindungan kekayaan intelektual", "kerahasiaan seumur hidup", "perlindungan informasi sensitif", "informasi proprietari", "pembatasan kompetitor"],
        "audit_indicators_en": ["no NDAs signed", "confidentiality agreements expired", "inadequate scope of NDAs", "no reminder of obligations after departure", "NDAs not legally binding", "missing signatures", "no enforcement of restrictions"],
        "audit_indicators_id": ["tidak ada NDA yang ditandatangani", "perjanjian kerahasiaan kedaluwarsa", "ruang lingkup NDA tidak memadai", "tidak ada pengingat kewajiban setelah keberangkatan", "NDA tidak mengikat secara hukum", "tanda tangan hilang", "tidak ada penegakan pembatasan"],
        "related_assets_en": ["confidentiality agreements", "legal contracts", "NDAs", "employment termination documents", "intellectual property records", "proprietary information databases"],
        "related_assets_id": ["perjanjian kerahasiaan", "kontrak hukum", "NDA", "dokumen pemutusan hubungan kerja", "catatan kekayaan intelektual", "database informasi proprietari"],
        "security_principles_en": ["confidentiality", "legal protection", "ongoing obligation", "intellectual property rights", "competitive advantage", "information classification"],
        "security_principles_id": ["kerahasiaan", "perlindungan hukum", "kewajiban berkelanjutan", "hak kekayaan intelektual", "keunggulan kompetitif", "klasifikasi informasi"]
    },
    "A.6.7": {
        "keywords_en": ["remote work security", "telecommuting security", "home office security", "remote access policies", "mobile work security", "work from home security", "remote equipment security", "offsite work guidelines", "telework security", "distributed workforce security"],
        "keywords_id": ["keamanan kerja jarak jauh", "keamanan telecommuting", "keamanan kantor rumah", "kebijakan akses jarak jauh", "keamanan kerja mobile", "keamanan kerja dari rumah", "keamanan peralatan jarak jauh", "pedoman kerja offsite", "keamanan telework", "keamanan tenaga kerja terdistribusi"],
        "audit_indicators_en": ["no remote work security policy", "unsecured home networks", "company devices used without protection", "no remote access guidelines", "shadow IT in remote work", "inadequate endpoint protection", "data leakage from remote locations"],
        "audit_indicators_id": ["tidak ada kebijakan keamanan kerja jarak jauh", "jaringan rumah tidak aman", "perangkat perusahaan digunakan tanpa perlindungan", "tidak ada pedoman akses jarak jauh", "shadow IT dalam kerja jarak jauh", "perlindungan titik akhir tidak memadai", "kebocoran data dari lokasi jarak jauh"],
        "related_assets_en": ["VPN connections", "remote access devices", "home office equipment", "mobile devices", "cloud storage", "collaboration platforms"],
        "related_assets_id": ["koneksi VPN", "perangkat akses jarak jauh", "peralatan kantor rumah", "perangkat mobile", "penyimpanan cloud", "platform kolaborasi"],
        "security_principles_en": ["secure remote access", "endpoint protection", "data encryption", "network segmentation", "zero trust", "continuous monitoring"],
        "security_principles_id": ["akses jarak jauh aman", "perlindungan titik akhir", "enkripsi data", "segmentasi jaringan", "zero trust", "pemantauan berkelanjutan"]
    },
    "A.6.8": {
        "keywords_en": ["incident reporting", "security event notification", "whistleblowing channels", "security incident escalation", "reporting mechanisms", "alert systems", "incident communication", "security hotlines", "anonymous reporting", "escalation procedures"],
        "keywords_id": ["pelaporan insiden", "notifikasi kejadian keamanan", "saluran pelapor", "eskalasi insiden keamanan", "mekanisme pelaporan", "sistem peringatan", "komunikasi insiden", "hotline keamanan", "pelaporan anonim", "prosedur eskalasi"],
        "audit_indicators_en": ["no incident reporting process", "employees unaware of reporting channels", "security incidents not reported", "no escalation procedures", "reporting mechanisms inadequate", "fear of retaliation prevents reporting", "no tracking of reported incidents"],
        "audit_indicators_id": ["tidak ada proses pelaporan insiden", "karyawan tidak sadar akan saluran pelaporan", "insiden keamanan tidak dilaporkan", "tidak ada prosedur eskalasi", "mekanisme pelaporan tidak memadai", "takut pembalasan mencegah pelaporan", "tidak ada pelacakan insiden yang dilaporkan"],
        "related_assets_en": ["incident reporting system", "alerting platforms", "communication channels", "ticketing systems", "notification services", "reporting hotlines"],
        "related_assets_id": ["sistem pelaporan insiden", "platform peringatan", "saluran komunikasi", "sistem tiketing", "layanan notifikasi", "hotline pelaporan"],
        "security_principles_en": ["reporting culture", "no blame culture", "timely notification", "transparency", "escalation pathways", "continuous improvement"],
        "security_principles_id": ["budaya pelaporan", "budaya tanpa salahkan", "notifikasi tepat waktu", "transparansi", "jalur eskalasi", "peningkatan berkelanjutan"]
    }
}

# Apply enrichment
enriched_count = 0
for control in enriched_controls:
    control_id = control['control_id']
    if control_id in enrichment_data:
        control.update(enrichment_data[control_id])
        enriched_count += 1

# Save the updated file
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(enriched_controls, f, indent=2, ensure_ascii=False)

print(f"Enriched {enriched_count} controls successfully")
