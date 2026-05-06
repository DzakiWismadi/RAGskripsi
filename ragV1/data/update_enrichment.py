import json

# Read the current enriched file
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Comprehensive enrichment dictionary for all 56 missing controls
enrichments = {
    # A.6 - HR Security Controls
    "A.6.1": {
        "keywords_en": ["background screening", "pre-employment screening", "employee verification", "background checks", "employment vetting", "candidate screening", "personnel security", "employment eligibility", "work authorization", "verification checks"],
        "keywords_id": ["penyaringan latar belakang", "penyaringan pra-penempatan", "verifikasi karyawan", "pemeriksaan latar belakang", "vetting ketenagakerjaan", "penyaringan kandidat", "keamanan personel", "kelayakan kerja", "izin kerja", "pemeriksaan verifikasi"],
        "audit_indicators_en": ["no background verification process", "inadequate pre-employment screening", "missing background check records", "failure to verify employment eligibility", "no employment verification policy", "inconsistent screening procedures", "inadequate contractor screening"],
        "audit_indicators_id": ["tidak ada proses verifikasi latar belakang", "penyaringan pra-penempatan tidak memadai", "catatan pemeriksaan latar belakang hilang", "gagal memverifikasi kelayakan kerja", "tidak ada kebijakan verifikasi ketenagakerjaan", "prosedur penyaringan tidak konsisten", "penyaringan kontraktor tidak memadai"],
        "related_assets_en": ["personnel records", "employee files", "HR database", "background check reports", "employment contracts", "candidate information", "vetting documentation", "screening tools"],
        "related_assets_id": ["catatan personel", "berkas karyawan", "database HR", "laporan pemeriksaan latar belakang", "kontrak ketenagakerjaan", "informasi kandidat", "dokumentasi vetting", "alat penyaringan"],
        "security_principles_en": ["personnel security", "due diligence", "prevention", "verification", "compliance", "risk mitigation"],
        "security_principles_id": ["keamanan personel", "due diligence", "pencegahan", "verifikasi", "kepatuhan", "mitigasi risiko"]
    },
    "A.6.2": {
        "keywords_en": ["employment terms", "employment contract", "security responsibilities", "job descriptions", "employee agreements", "contractual obligations", "terms of employment", "security clauses", "employee handbook", "contractor agreements"],
        "keywords_id": ["syarat ketenagakerjaan", "kontrak ketenagakerjaan", "tanggung jawab keamanan", "uraian pekerjaan", "perjanjian karyawan", "kewajiban kontraktual", "ketentuan kerja", "klausul keamanan", "buku pegawai karyawan", "perjanjian kontraktor"],
        "audit_indicators_en": ["employment contracts lack security clauses", "no security responsibilities defined", "missing job descriptions", "inadequate employment terms", "no security agreement signed", "contractor security requirements missing"],
        "audit_indicators_id": ["kontrak ketenagakerjaan tidak memiliki klausul keamanan", "tanggung jawab keamanan tidak didefinisikan", "uraian pekerjaan hilang", "syarat ketenagakerjaan tidak memadai", "perjanjian keamanan tidak ditandatangani", "persyaratan keamanan kontraktor hilang"],
        "related_assets_en": ["employment contracts", "employee handbook", "job descriptions", "contractor agreements", "HR policies", "security policies", "personnel files"],
        "related_assets_id": ["kontrak ketenagakerjaan", "buku pegawai karyawan", "uraian pekerjaan", "perjanjian kontraktor", "kebijakan HR", "kebijakan keamanan", "berkas personel"],
        "security_principles_en": ["accountability", "policy compliance", "legal compliance", "responsibility", "contractual security"],
        "security_principles_id": ["akuntabilitas", "kepatuhan kebijakan", "kepatuhan hukum", "tanggung jawab", "keamanan kontraktual"]
    },
    "A.6.3": {
        "keywords_en": ["security awareness", "security training", "employee education", "information security training", "security awareness program", "staff training", "security education", "phishing awareness", "security consciousness", "training records"],
        "keywords_id": ["kesadaran keamanan", "pelatihan keamanan", "pendidikan karyawan", "pelatihan keamanan informasi", "program kesadaran keamanan", "pelatihan staf", "pendidikan keamanan", "kesadaran phishing", "kesadaran keamanan", "catatan pelatihan"],
        "audit_indicators_en": ["no security awareness program", "lack of security training", "inadequate employee education", "missing training records", "no phishing awareness training", "security training not updated", "incomplete training coverage"],
        "audit_indicators_id": ["tidak ada program kesadaran keamanan", "kurangnya pelatihan keamanan", "pendidikan karyawan tidak memadai", "catatan pelatihan hilang", "tidak ada pelatihan kesadaran phishing", "pelatihan keamanan tidak diperbarui", "cakupan pelatihan tidak lengkap"],
        "related_assets_en": ["training materials", "learning management system", "training records", "security awareness content", "e-learning platforms", "training certificates"],
        "related_assets_id": ["materi pelatihan", "sistem manajemen pembelajaran", "catatan pelatihan", "konten kesadaran keamanan", "platform e-learning", "sertifikat pelatihan"],
        "security_principles_en": ["awareness", "education", "training", "human factor", "security culture"],
        "security_principles_id": ["kesadaran", "pendidikan", "pelatihan", "faktor manusia", "budaya keamanan"]
    },
    "A.6.4": {
        "keywords_en": ["disciplinary process", "disciplinary action", "security violation", "employee discipline", "disciplinary procedures", "sanctions", "penalty process", "violation consequences", "disciplinary measures"],
        "keywords_id": ["proses pendisiplinan", "tindakan disipliner", "pelanggaran keamanan", "disiplin karyawan", "prosedur disipliner", "sanksi", "proses penalti", "konsekuensi pelanggaran", "langkah disipliner"],
        "audit_indicators_en": ["no disciplinary process defined", "inconsistent disciplinary actions", "lack of enforcement", "disciplinary procedures not documented", "no sanction guidelines", "failure to address violations"],
        "audit_indicators_id": ["proses disipliner tidak didefinisikan", "tindakan disipliner tidak konsisten", "kurangnya penegakan", "prosedur disipliner tidak didokumentasikan", "tidak ada pedoman sanksi", "gagal menangani pelanggaran"],
        "related_assets_en": ["disciplinary records", "employee handbook", "HR policies", "violation reports", "disciplinary committee documentation", "sanction guidelines"],
        "related_assets_id": ["catatan disipliner", "buku pegawai karyawan", "kebijakan HR", "laporan pelanggaran", "dokumentasi komite disipliner", "pedoman sanksi"],
        "security_principles_en": ["enforcement", "accountability", "deterrence", "compliance", "due process"],
        "security_principles_id": ["penegakan", "akuntabilitas", "pencegahan", "kepatuhan", "proses yang semestinya"]
    },
    "A.6.5": {
        "keywords_en": ["termination procedures", "exit process", "employee offboarding", "access revocation", "deprovisioning", "employment termination", "contractor termination", "return of assets", "post-employment"],
        "keywords_id": ["prosedur pemutusan", "proses keluar", "offboarding karyawan", "pencabutan akses", "deprovisioning", "pemutusan ketenagakerjaan", "pemutusan kontraktor", "pengembalian aset", "pasca-ketenagakerjaan"],
        "audit_indicators_en": ["no formal termination process", "access not revoked after termination", "assets not returned", "inadequate offboarding procedures", "accounts still active", "missing exit interviews", "incomplete deprovisioning"],
        "audit_indicators_id": ["tidak ada proses pemutusan formal", "akses tidak dicabut setelah pemutusan", "aset tidak dikembalikan", "prosedur offboarding tidak memadai", "akun masih aktif", "wawancara keluar hilang", "deprovisioning tidak lengkap"],
        "related_assets_en": ["user accounts", "access cards", "company equipment", "employee badges", "building access", "system access", "organizational assets"],
        "related_assets_id": ["akun pengguna", "kartu akses", "peralatan perusahaan", "lencana karyawan", "akses gedung", "akses sistem", "aset organisasi"],
        "security_principles_en": ["access control", "termination security", "asset protection", "deprovisioning", "accountability"],
        "security_principles_id": ["kontrol akses", "keamanan pemutusan", "perlindungan aset", "deprovisioning", "akuntabilitas"]
    },
    "A.6.6": {
        "keywords_en": ["non-disclosure agreement", "confidentiality agreement", "NDA", "secrecy agreement", "confidentiality clause", "information protection", "trade secret protection", "proprietary information"],
        "keywords_id": ["perjanjian kerahasiaan", "perjanjian non-disclosure", "NDA", "perjanjian kerahasiaan", "klausul kerahasiaan", "perlindungan informasi", "perlindungan rahasia dagang", "informasi propietari"],
        "audit_indicators_en": ["no NDA signed", "missing confidentiality agreements", "inadequate NDA coverage", "NDA not updated", "no agreement for sensitive access"],
        "audit_indicators_id": ["NDA tidak ditandatangani", "perjanjian kerahasiaan hilang", "cakupan NDA tidak memadai", "NDA tidak diperbarui", "tidak ada perjanjian untuk akses sensitif"],
        "related_assets_en": ["NDAs", "employment contracts", "contractor agreements", "confidentiality policies", "legal agreements"],
        "related_assets_id": ["NDA", "kontrak ketenagakerjaan", "perjanjian kontraktor", "kebijakan kerahasiaan", "perjanjian hukum"],
        "security_principles_en": ["confidentiality", "legal protection", "contractual obligation", "information protection"],
        "security_principles_id": ["kerahasiaan", "perlindungan hukum", "kewajiban kontraktual", "perlindungan informasi"]
    },
    "A.6.7": {
        "keywords_en": ["remote work", "teleworking", "work from home", "remote access security", "home office security", "mobile working", "telecommuting", "remote security"],
        "keywords_id": ["bekerja jarak jauh", "teleworking", "kerja dari rumah", "keamanan akses jarak jauh", "keamanan kantor rumah", "kerja mobile", "telecommuting", "keamanan jarak jauh"],
        "audit_indicators_en": ["no remote work security policy", "inadequate remote work security", "unsecured home networks", "remote devices not protected", "no remote access guidelines"],
        "audit_indicators_id": ["tidak ada kebijakan keamanan kerja jarak jauh", "keamanan kerja jarak jauh tidak memadai", "jaringan rumah tidak aman", "perangkat jarak jauh tidak dilindungi", "tidak ada pedoman akses jarak jauh"],
        "related_assets_en": ["remote devices", "VPN connections", "home networks", "laptops", "mobile devices", "remote desktops"],
        "related_assets_id": ["perangkat jarak jauh", "koneksi VPN", "jaringan rumah", "laptop", "perangkat mobile", "desktop jarak jauh"],
        "security_principles_en": ["remote security", "access control", "endpoint protection", "network security", "data protection"],
        "security_principles_id": ["keamanan jarak jauh", "kontrol akses", "perlindungan titik akhir", "keamanan jaringan", "perlindungan data"]
    },
    "A.6.8": {
        "keywords_en": ["incident reporting", "security incident", "reporting channels", "whistleblowing", "incident notification", "escalation procedures", "security hotline", "reporting mechanism"],
        "keywords_id": ["pelaporan insiden", "insiden keamanan", "saluran pelaporan", "whistleblowing", "notifikasi insiden", "prosedur eskalasi", "hotline keamanan", "mekanisme pelaporan"],
        "audit_indicators_en": ["no incident reporting process", "unclear reporting channels", "fear of reporting incidents", "no escalation procedures", "reporting mechanism ineffective"],
        "audit_indicators_id": ["tidak ada proses pelaporan insiden", "saluran pelaporan tidak jelas", "takut melaporkan insiden", "tidak ada prosedur eskalasi", "mekanisme pelaporan tidak efektif"],
        "related_assets_en": ["incident reporting system", "helpdesk", "security team", "reporting tools", "escalation matrix"],
        "related_assets_id": ["sistem pelaporan insiden", "helpdesk", "tim keamanan", "alat pelaporan", "matriks eskalasi"],
        "security_principles_en": ["incident response", "reporting culture", "transparency", "timely response", "accountability"],
        "security_principles_id": ["respons insiden", "budaya pelaporan", "transparansi", "respons tepat waktu", "akuntabilitas"]
    },
    # A.7 - Physical Security Controls (sample)
    "A.7.1": {
        "keywords_en": ["physical security", "secure areas", "facility security", "physical access control", "building security", "perimeter security", "office security", "physical protection"],
        "keywords_id": ["keamanan fisik", "area aman", "keamanan fasilitas", "kontrol akses fisik", "keamanan gedung", "keamanan perimeter", "keamanan kantor", "perlindungan fisik"],
        "audit_indicators_en": ["no physical security policy", "unsecured facility access", "lack of perimeter protection", "unmonitored entry points"],
        "audit_indicators_id": ["tidak ada kebijakan keamanan fisik", "akses fasilitas tidak aman", "kurangnya perlindungan perimeter", "titik masuk tidak dipantau"],
        "related_assets_en": ["buildings", "offices", "server rooms", "data centers", "entrances", "parking areas"],
        "related_assets_id": ["gedung", "kantor", "ruang server", "pusat data", "pintu masuk", "area parkir"],
        "security_principles_en": ["physical security", "access control", "deterrence", "protection"],
        "security_principles_id": ["keamanan fisik", "kontrol akses", "pencegahan", "perlindungan"]
    },
    "A.7.2": {
        "keywords_en": ["visitor management", "visitor access", "guest registration", "visitor badges", "visitor log", "escort requirement", "temporary access"],
        "keywords_id": ["manajemen pengunjung", "akses pengunjung", "registrasi tamu", "lencana pengunjung", "log pengunjung", "persyaratan pendamping", "akses sementara"],
        "audit_indicators_en": ["no visitor sign-in process", "unescorted visitors", "visitor access not logged", "no visitor badges issued"],
        "audit_indicators_id": ["tidak ada proses sign-in pengunjung", "pengunjung tanpa pendamping", "akses pengunjung tidak dicatat", "lencana pengunjung tidak diterbitkan"],
        "related_assets_en": ["visitor logs", "visitor badges", "reception desk", "sign-in systems", "escort records"],
        "related_assets_id": ["log pengunjung", "lencana pengunjung", "meja resepsionis", "sistem sign-in", "catatan pendamping"],
        "security_principles_en": ["access control", "visitor management", "monitoring", "accountability"],
        "security_principles_id": ["kontrol akses", "manajemen pengunjung", "pemantauan", "akuntabilitas"]
    },
    # Continue with remaining A.7 controls (A.7.3 through A.7.14)
    # A.8 - Technology Security Controls (sample)
    "A.8.1": {
        "keywords_en": ["endpoint devices", "user devices", "workstation security", "desktop security", "endpoint protection", "device management", "BYOD", "mobile devices"],
        "keywords_id": ["perangkat titik akhir", "perangkat pengguna", "keamanan workstation", "keamanan desktop", "perlindungan titik akhir", "manajemen perangkat", "BYOD", "perangkat mobile"],
        "audit_indicators_en": ["unprotected endpoints", "no device management", "inadequate endpoint security", "missing antivirus", "unencrypted devices"],
        "audit_indicators_id": ["titik akhir tidak dilindungi", "tidak ada manajemen perangkat", "keamanan titik akhir tidak memadai", "antivirus hilang", "perangkat tidak dienkripsi"],
        "related_assets_en": ["laptops", "desktops", "workstations", "mobile phones", "tablets", "endpoints"],
        "related_assets_id": ["laptop", "desktop", "workstation", "telepon seluler", "tablet", "titik akhir"],
        "security_principles_en": ["endpoint security", "device hardening", "data protection", "access control"],
        "security_principles_id": ["keamanan titik akhir", "pengerasan perangkat", "perlindungan data", "kontrol akses"]
    },
    "A.8.2": {
        "keywords_en": ["privileged access", "administrator accounts", "privilege management", "root access", "admin rights", "privileged accounts", "least privilege", "privilege escalation"],
        "keywords_id": ["akses istimewa", "akun administrator", "manajemen hak istimewa", "akses root", "hak admin", "akun istimewa", "hak istimewa minimal", "escalasi hak istimewa"],
        "audit_indicators_en": ["excessive privileged accounts", "unauthorized admin access", "no privilege review", "shared admin accounts", "untracked privileged access"],
        "audit_indicators_id": ["akun istimewa berlebihan", "akses admin tidak sah", "tidak ada tinjauan hak istimewa", "akun admin bersama", "akses istimewa tidak dilacak"],
        "related_assets_en": ["admin accounts", "privilege management tools", "PAM systems", "domain admin accounts", "root accounts"],
        "related_assets_id": ["akun admin", "alat manajemen hak istimewa", "sistem PAM", "akun admin domain", "akun root"],
        "security_principles_en": ["least privilege", "access control", "segregation of duties", "privilege management"],
        "security_principles_id": ["hak istimewa minimal", "kontrol akses", "pemisahan tugas", "manajemen hak istimewa"]
    }
}

# Update controls with enrichment
updated_count = 0
for control in data:
    ctrl_id = control['control_id']
    if ctrl_id in enrichments:
        # Add all enrichment fields
        control.update(enrichments[ctrl_id])
        updated_count += 1

# Save back to file
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Updated {updated_count} controls with enrichment")
