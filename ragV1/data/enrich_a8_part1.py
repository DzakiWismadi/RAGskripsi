import json

# Read the enriched controls
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    controls = json.load(f)

# A.8 enrichments (part 1: A.8.1 - A.8.12)
a8_enrichments_part1 = {
    "A.8.1": {
        "keywords_en": ["endpoint devices", "user device management", "mobile device security", "device encryption", "BYOD policy", "endpoint protection", "device registration", "mobile device management", "device hardening", "endpoint security controls"],
        "keywords_id": ["perangkat titik akhir", "manajemen perangkat pengguna", "keamanan perangkat seluler", "enkripsi perangkat", "kebijakan BYOD", "perlindungan titik akhir", "registrasi perangkat", "manajemen perangkat mobile", "pengerasan perangkat", "kendali keamanan titik akhir"],
        "audit_indicators_en": ["unmanaged endpoint devices detected", "no mobile device management solution", "devices lack encryption", "no BYOD policy exists", "endpoint protection not installed", "unregistered devices on network", "outdated device operating systems", "no device inventory"],
        "audit_indicators_id": ["perangkat titik akhir tidak terkelola terdeteksi", "tidak ada solusi manajemen perangkat mobile", "perangkat tidak memiliki enkripsi", "tidak ada kebijakan BYOD", "perlindungan titik akhir tidak diinstal", "perangkat tidak terdaftar di jaringan", "sistem operasi perangkat usang", "tidak ada inventaris perangkat"],
        "related_assets_en": ["laptops", "smartphones", "tablets", "mobile devices", "USB drives", "endpoint protection software", "MDM solution", "encryption software"],
        "related_assets_id": ["laptop", "smartphone", "tablet", "perangkat seluler", "USB drive", "perangkat lunak perlindungan titik akhir", "solusi MDM", "perangkat lunak enkripsi"],
        "security_principles_en": ["Defense in Depth", "Least Privilege", "Data Protection", "Asset Management", "Endpoint Security"],
        "security_principles_id": ["Pertahanan Berlapis", "Hak Minimum", "Perlindungan Data", "Manajemen Aset", "Keamanan Titik Akhir"]
    },
    "A.8.2": {
        "keywords_en": ["privileged access rights", "privilege management", "admin accounts", "root access", "privileged account management", "access control", "privilege escalation", "role-based access control", "least privilege", "privileged session monitoring"],
        "keywords_id": ["hak akses istimewa", "manajemen hak istimewa", "akun administrator", "akses root", "manajemen akun istimewa", "kendali akses", "escalasi hak istimewa", "kendali akses berbasis peran", "hak minimum", "pemantauan sesi istimewa"],
        "audit_indicators_en": ["excessive privileged users", "no privileged access review process", "privilege accounts shared", "no monitoring of admin sessions", "inactive privileged accounts not disabled", "lack of privilege recertification"],
        "audit_indicators_id": ["pengguna istimewa berlebihan", "tidak ada proses tinjauan akses istimewa", "akun istimewa dibagikan", "tidak ada pemantauan sesi admin", "akun istimewa tidak aktif tidak dinonaktifkan", "kurangnya resertifikasi hak istimewa"],
        "related_assets_en": ["admin accounts", "privileged accounts", "access management systems", "privileged session recording", "PAM solution"],
        "related_assets_id": ["akun administrator", "akun istimewa", "sistem manajemen akses", "rekaman sesi istimewa", "solusi PAM"],
        "security_principles_en": ["Least Privilege", "Separation of Duties", "Accountability", "Access Control", "Privilege Management"],
        "security_principles_id": ["Hak Minimum", "Pemisahan Tugas", "Akuntabilitas", "Kendali Akses", "Manajemen Hak Istimewa"]
    },
    "A.8.3": {
        "keywords_en": ["access restriction", "information access control", "need-to-know basis", "access control policy", "data access restrictions", "authorization", "access control lists", "information classification", "access rights", "permission management"],
        "keywords_id": ["pembatasan akses", "kendali akses informasi", "dasar perlu diketahui", "kebijakan kendali akses", "pembatasan akses data", "otorisasi", "daftar kendali akses", "klasifikasi informasi", "hak akses", "manajemen izin"],
        "audit_indicators_en": ["users have access to unnecessary data", "access not based on job function", "no periodic access reviews", "excessive access privileges detected", "lack of access request documentation"],
        "audit_indicators_id": ["pengguna memiliki akses ke data yang tidak diperlukan", "akses tidak berdasarkan fungsi pekerjaan", "tidak ada tinjauan akses berkala", "hak akses berlebihan terdeteksi", "kurangnya dokumentasi permintaan akses"],
        "related_assets_en": ["file systems", "databases", "applications", "access control systems", "directory services"],
        "related_assets_id": ["sistem file", "basis data", "aplikasi", "sistem kendali akses", "layanan direktori"],
        "security_principles_en": ["Least Privilege", "Need to Know", "Access Control", "Data Confidentiality", "Authorization"],
        "security_principles_id": ["Hak Minimum", "Perlu Diketahui", "Kendali Akses", "Kerahasiaan Data", "Otorisasi"]
    },
    "A.8.4": {
        "keywords_en": ["source code access", "code repositories", "development environment security", "version control", "code access controls", "developer access", "source code protection", "Git security", "code repository management", "development security"],
        "keywords_id": ["akses kode sumber", "repositori kode", "keamanan lingkungan pengembangan", "kendali versi", "kendali akses kode", "akses pengembang", "perlindungan kode sumber", "keamanan Git", "manajemen repositori kode", "keamanan pengembangan"],
        "audit_indicators_en": ["unrestricted source code access", "no code review process", "developers have production access", "source code not version controlled", "no separation of development and production environments"],
        "audit_indicators_id": ["akses kode sumber tidak dibatasi", "tidak ada proses tinjauan kode", "pengembang memiliki akses produksi", "kode sumber tidak dikendalikan versinya", "tidak ada pemisahan lingkungan pengembangan dan produksi"],
        "related_assets_en": ["source code repositories", "version control systems", "development servers", "IDE tools", "code review tools"],
        "related_assets_id": ["repositori kode sumber", "sistem kendali versi", "server pengembangan", "alat IDE", "alat tinjauan kode"],
        "security_principles_en": ["Change Management", "Segregation of Duties", "Access Control", "Version Control", "Development Security"],
        "security_principles_id": ["Manajemen Perubahan", "Pemisahan Tugas", "Kendali Akses", "Kendali Versi", "Keamanan Pengembangan"]
    },
    "A.8.5": {
        "keywords_en": ["secure authentication", "multi-factor authentication", "MFA", "strong passwords", "authentication mechanisms", "identity verification", "login security", "authentication protocols", "credential management", "biometric authentication"],
        "keywords_id": ["autentikasi aman", "autentikasi multi-faktor", "MFA", "kata sandi kuat", "mekanisme autentikasi", "verifikasi identitas", "keamanan login", "protokol autentikasi", "manajemen kredensial", "autentikasi biometrik"],
        "audit_indicators_en": ["weak password policy", "no multi-factor authentication", "accounts without passwords", "authentication not required for sensitive access", "default credentials in use"],
        "audit_indicators_id": ["kebijakan kata sandi lemah", "tidak ada autentikasi multi-faktor", "akun tanpa kata sandi", "autentikasi tidak diperlukan untuk akses sensitif", "kredensial default digunakan"],
        "related_assets_en": ["authentication servers", "MFA devices", "password management tools", "authentication systems", "identity providers"],
        "related_assets_id": ["server autentikasi", "perangkat MFA", "alat manajemen kata sandi", "sistem autentikasi", "penyedia identitas"],
        "security_principles_en": ["Authentication", "Identity Verification", "Access Control", "Strong Cryptography", "Multi-Factor Security"],
        "security_principles_id": ["Autentikasi", "Verifikasi Identitas", "Kendali Akses", "Kriptografi Kuat", "Keamanan Multi-Faktor"]
    },
    "A.8.6": {
        "keywords_en": ["capacity management", "resource planning", "performance monitoring", "scalability", "system capacity", "storage capacity", "network capacity", "capacity forecasting", "resource utilization", "capacity planning"],
        "keywords_id": ["manajemen kapasitas", "perencanaan sumber daya", "pemantauan kinerja", "skalabilitas", "kapasitas sistem", "kapasitas penyimpanan", "kapasitas jaringan", "peramalan kapasitas", "utilisasi sumber daya", "perencanaan kapasitas"],
        "audit_indicators_en": ["no capacity planning process", "system performance issues due to capacity", "no monitoring of resource utilization", "lack of capacity forecasting", "unplanned system outages due to capacity"],
        "audit_indicators_id": ["tidak ada proses perencanaan kapasitas", "masalah kinerja sistem karena kapasitas", "tidak ada pemantauan utilisasi sumber daya", "kurangnya peramalan kapasitas", "gangguan sistem yang tidak direncanakan karena kapasitas"],
        "related_assets_en": ["servers", "storage systems", "network infrastructure", "monitoring tools", "capacity planning tools"],
        "related_assets_id": ["server", "sistem penyimpanan", "infrastruktur jaringan", "alat pemantauan", "alat perencanaan kapasitas"],
        "security_principles_en": ["Availability", "Performance Management", "Resource Planning", "Service Continuity", "Operational Excellence"],
        "security_principles_id": ["Ketersediaan", "Manajemen Kinerja", "Perencanaan Sumber Daya", "Kelangsungan Layanan", "Keunggulan Operasional"]
    },
    "A.8.7": {
        "keywords_en": ["malware protection", "antivirus software", "anti-malware", "endpoint protection", "malware detection", "virus scanning", "malware prevention", "security software", "threat protection", "malicious software prevention"],
        "keywords_id": ["perlindungan malware", "perangkat lunak antivirus", "anti-malware", "perlindungan titik akhir", "deteksi malware", "pemindaian virus", "pencegahan malware", "perangkat lunak keamanan", "perlindungan ancaman", "pencegahan perangkat lunak berbahaya"],
        "audit_indicators_en": ["no antivirus software installed", "antivirus definitions outdated", "malware protection disabled", "no scheduled malware scans", "systems infected with malware"],
        "audit_indicators_id": ["tidak ada perangkat lunak antivirus yang diinstal", "definisi antivirus usang", "perlindungan malware dinonaktifkan", "tidak ada pemindaian malware terjadwal", "sistem terinfeksi malware"],
        "related_assets_en": ["antivirus software", "endpoint protection platforms", "malware scanning tools", "security appliances", "threat detection systems"],
        "related_assets_id": ["perangkat lunak antivirus", "platform perlindungan titik akhir", "alat pemindaian malware", "appliance keamanan", "sistem deteksi ancaman"],
        "security_principles_en": ["Defense in Depth", "Threat Prevention", "System Integrity", "Malware Defense", "Endpoint Protection"],
        "security_principles_id": ["Pertahanan Berlapis", "Pencegahan Ancaman", "Integritas Sistem", "Pertahanan Malware", "Perlindungan Titik Akhir"]
    },
    "A.8.8": {
        "keywords_en": ["vulnerability management", "security patches", "vulnerability scanning", "patch management", "security updates", "vulnerability assessment", "technical vulnerabilities", "security remediation", "CVE management", "vulnerability tracking"],
        "keywords_id": ["manajemen kerentanan", "patch keamanan", "pemindaian kerentanan", "manajemen patch", "pembaruan keamanan", "penilaian kerentanan", "kerentanan teknis", "remediasi keamanan", "manajemen CVE", "pelacakan kerentanan"],
        "audit_indicators_en": ["no vulnerability scanning process", "unpatched systems detected", "no patch management policy", "critical vulnerabilities not addressed", "outdated software versions"],
        "audit_indicators_id": ["tidak ada proses pemindaian kerentanan", "sistem tidak dipatch terdeteksi", "tidak ada kebijakan manajemen patch", "kerentanan kritis tidak ditangani", "versi perangkat lunak usang"],
        "related_assets_en": ["vulnerability scanners", "patch management tools", "security update systems", "vulnerability databases", "remediation tools"],
        "related_assets_id": ["pemindai kerentanan", "alat manajemen patch", "sistem pembaruan keamanan", "basis data kerentanan", "alat remediasi"],
        "security_principles_en": ["Vulnerability Management", "Continuous Monitoring", "Patch Management", "Security Maintenance", "Risk Remediation"],
        "security_principles_id": ["Manajemen Kerentanan", "Pemantauan Berkelanjutan", "Manajemen Patch", "Pemeliharaan Keamanan", "Remediasi Risiko"]
    },
    "A.8.9": {
        "keywords_en": ["configuration management", "system configuration", "security configuration", "configuration baseline", "change control", "configuration drift", "hardening standards", "security baselines", "system hardening", "configuration control"],
        "keywords_id": ["manajemen konfigurasi", "konfigurasi sistem", "konfigurasi keamanan", "baseline konfigurasi", "kendali perubahan", "konfigurasi drift", "standar pengerasan", "baseline keamanan", "pengerasan sistem", "kendali konfigurasi"],
        "audit_indicators_en": ["inconsistent security configurations", "no configuration baseline", "unauthorized configuration changes", "configuration drift detected", "no hardening standards applied"],
        "audit_indicators_id": ["konfigurasi keamanan tidak konsisten", "tidak ada baseline konfigurasi", "perubahan konfigurasi tidak sah", "konfigurasi drift terdeteksi", "tidak ada standar pengerasan diterapkan"],
        "related_assets_en": ["configuration management tools", "system hardening guides", "baseline configurations", "change management systems", "configuration monitoring tools"],
        "related_assets_id": ["alat manajemen konfigurasi", "panduan pengerasan sistem", "konfigurasi baseline", "sistem manajemen perubahan", "alat pemantauan konfigurasi"],
        "security_principles_en": ["Configuration Management", "Change Control", "System Hardening", "Security Baselines", "Standardization"],
        "security_principles_id": ["Manajemen Konfigurasi", "Kendali Perubahan", "Pengerasan Sistem", "Baseline Keamanan", "Standardisasi"]
    },
    "A.8.10": {
        "keywords_en": ["information deletion", "data sanitization", "secure deletion", "data disposal", "media sanitization", "data wiping", "secure data destruction", "storage media disposal", "data remanence", "information disposal"],
        "keywords_id": ["penghapusan informasi", "sanitasi data", "penghapusan aman", "pembuangan data", "sanitasi media", "penghapusan data", "penghancuran data aman", "pembuangan media penyimpanan", "remanensi data", "pembuangan informasi"],
        "audit_indicators_en": ["sensitive data not securely deleted", "no data sanitization process", "storage devices disposed without wiping", "data remnants found on discarded media", "no secure deletion procedures"],
        "audit_indicators_id": ["data sensitif tidak dihapus dengan aman", "tidak ada proses sanitasi data", "perangkat penyimpanan dibuang tanpa penghapusan", "sisa data ditemukan pada media yang dibuang", "tidak ada prosedur penghapusan aman"],
        "related_assets_en": ["storage media", "hard drives", "backup tapes", "USB devices", "data wiping tools"],
        "related_assets_id": ["media penyimpanan", "hard drive", "pita backup", "perangkat USB", "alat penghapusan data"],
        "security_principles_en": ["Data Privacy", "Secure Disposal", "Data Sanitization", "Media Protection", "Information Lifecycle"],
        "security_principles_id": ["Privasi Data", "Pembuangan Aman", "Sanitasi Data", "Perlindungan Media", "Siklus Hidup Informasi"]
    },
    "A.8.11": {
        "keywords_en": ["data masking", "data obfuscation", "data anonymization", "test data management", "privacy protection", "data de-identification", "sensitive data protection", "production data protection", "data privacy", "data pseudonymization"],
        "keywords_id": ["penyamaran data", "pengaburan data", "anonymisasi data", "manajemen data uji", "perlindungan privasi", "de-identifikasi data", "perlindungan data sensitif", "perlindungan data produksi", "privasi data", "pseudonymisasi data"],
        "audit_indicators_en": ["production data used in testing without masking", "no data masking procedures", "real PII in test environments", "sensitive data exposed in development", "lack of test data management"],
        "audit_indicators_id": ["data produksi digunakan dalam pengujian tanpa penyamaran", "tidak ada prosedur penyamaran data", "PII asli di lingkungan pengujian", "data sensitif terekspos di pengembangan", "kurangnya manajemen data uji"],
        "related_assets_en": ["test databases", "data masking tools", "anonymization software", "test data management platforms", "development environments"],
        "related_assets_id": ["basis data uji", "alat penyamaran data", "perangkat lunak anonymisasi", "platform manajemen data uji", "lingkungan pengembangan"],
        "security_principles_en": ["Data Privacy", "Privacy by Design", "Test Data Security", "PII Protection", "Data Minimization"],
        "security_principles_id": ["Privasi Data", "Privasi sejak Desain", "Keamanan Data Uji", "Perlindungan PII", "Minimasi Data"]
    },
    "A.8.12": {
        "keywords_en": ["data loss prevention", "DLP", "data leakage prevention", "data exfiltration", "sensitive data monitoring", "data protection", "DLP software", "data transfer control", "information leakage prevention", "data breach prevention"],
        "keywords_id": ["pencegahan kebocoran data", "DLP", "pencegahan kebocoran data", "ekstrfiltrasi data", "pemantauan data sensitif", "perlindungan data", "perangkat lunak DLP", "kendali transfer data", "pencegahan kebocoran informasi", "pencegahan pelanggaran data"],
        "audit_indicators_en": ["no DLP solution implemented", "sensitive data transferred without controls", "data exfiltration detected", "no monitoring of data transfers", "lack of data leakage prevention"],
        "audit_indicators_id": ["tidak ada solusi DLP yang diterapkan", "data sensitif ditransfer tanpa kendali", "ekstrfiltrasi data terdeteksi", "tidak ada pemantauan transfer data", "kurangnya pencegahan kebocoran data"],
        "related_assets_en": ["DLP software", "data monitoring tools", "email gateways", "network DLP appliances", "endpoint DLP agents"],
        "related_assets_id": ["perangkat lunak DLP", "alat pemantauan data", "gerbang email", "appliance DLP jaringan", "agen DLP titik akhir"],
        "security_principles_en": ["Data Protection", "Information Security", "Loss Prevention", "Data Privacy", "Monitoring and Detection"],
        "security_principles_id": ["Perlindungan Data", "Keamanan Informasi", "Pencegahan Kehilangan", "Privasi Data", "Pemantauan dan Deteksi"]
    }
}

# Apply enrichments to controls
enriched_count = 0
for control in controls:
    if control['control_id'] in a8_enrichments_part1:
        for key, value in a8_enrichments_part1[control['control_id']].items():
            control[key] = value
        enriched_count += 1

# Save the updated controls
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(controls, f, indent=2, ensure_ascii=False)

print(f"Enriched {enriched_count} A.8 controls (part 1)")
print("File saved successfully")
