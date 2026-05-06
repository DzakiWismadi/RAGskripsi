import json

# Load the original controls
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls.json', 'r', encoding='utf-8') as f:
    controls = json.load(f)

# Define enrichment for each control based on deep understanding of security domains
enrichments = {
    "A.5.1": {
        "keywords_en": ["information security policy", "security governance", "management commitment", "security framework", "policy approval", "policy communication", "policy review", "security objectives", "policy scope", "management approval"],
        "keywords_id": ["kebijakan keamanan informasi", "tata kelola keamanan", "komitmen manajemen", "kerangka kerja keamanan", "persetujuan kebijakan", "komunikasi kebijakan", "tinjauan kebijakan", "tujuan keamanan", "ruang lingkup kebijakan", "persetujuan manajemen"],
        "audit_indicators_en": ["no information security policy exists", "policy not approved by management", "policy not communicated to employees", "policy not reviewed annually", "policy lacks management signature", "policy outdated", "no policy distribution records", "policy not aligned with business requirements"],
        "audit_indicators_id": ["tidak ada kebijakan keamanan informasi", "kebijakan tidak disetujui manajemen", "kebijakan tidak dikomunikasikan ke karyawan", "kebijakan tidak ditinjau setiap tahun", "kebijakan tidak ada tanda tangan manajemen", "kebijakan kadaluarsa", "tidak ada rekam distribusi kebijakan", "kebijakan tidak selaras dengan persyaratan bisnis"],
        "related_assets_en": ["policy documents", "security governance framework", "management system documentation"],
        "related_assets_id": ["dokumen kebijakan", "kerangka kerja tata kelola keamanan", "dokumen sistem manajemen"],
        "security_principles_en": ["governance", "management commitment", "policy-driven security", "top-down approach"],
        "security_principles_id": ["tata kelola", "komitmen manajemen", "keamanan berbasis kebijakan", "pendekatan dari atas ke bawah"]
    },
    "A.5.2": {
        "keywords_en": ["roles and responsibilities", "security ownership", "defined responsibilities", "segregation of duties", "accountability", "security coordination", "role definitions", "responsibility allocation"],
        "keywords_id": ["peran dan tanggung jawab", "kepemilikan keamanan", "tanggung jawab terdefinisi", "pemisahan tugas", "akuntabilitas", "koordinasi keamanan", "definisi peran", "alokasi tanggung jawab"],
        "audit_indicators_en": ["security roles not defined", "responsibilities not assigned", "no security owner identified", "overlapping security responsibilities", "undefined escalation paths", "lack of accountability", "no role documentation"],
        "audit_indicators_id": ["peran keamanan tidak didefinisikan", "tanggung jawab tidak dialokasikan", "tidak ada pemilik keamanan", "tanggung jawab keamanan tumpang tindih", "jalur eskalasi tidak jelas", "kurang akuntabilitas", "tidak ada dokumentasi peran"],
        "related_assets_en": ["organizational charts", "job descriptions", "responsibility matrices", "security governance structure"],
        "related_assets_id": ["struktur organisasi", "deskripsi pekerjaan", "matriks tanggung jawab", "struktur tata kelola keamanan"],
        "security_principles_en": ["accountability", "separation of duties", "clear lines of authority", "defense in depth"],
        "security_principles_id": ["akuntabilitas", "pemisahan tugas", "garis wewenang yang jelas", "pertahanan berlapis"]
    },
    "A.5.3": {
        "keywords_en": ["segregation of duties", "conflict of interest", "dual control", "separation of privileges", "collusion prevention", "incompatible duties", "task separation", "duties segregation"],
        "keywords_id": ["pemisahan tugas", "konflik kepentingan", "kontrol ganda", "pemisahan hak akses", "pencegahan kolusi", "tugas yang tidak kompatibel", "pemisahan fungsi", "segregasi tugas"],
        "audit_indicators_en": ["single person has conflicting duties", "no segregation of sensitive tasks", "developer has production access", "same person initiates and approves transactions", "no dual control for critical operations", "incompatible functions combined"],
        "audit_indicators_id": ["satu orang memiliki tugas yang konflik", "tidak ada pemisahan tugas sensitif", "developer memiliki akses produksi", "orang yang sama menginisiasi dan menyetujui transaksi", "tidak ada kontrol ganda untuk operasi kritis", "fungsi yang tidak kompatibel digabung"],
        "related_assets_en": ["access control systems", "workflow management systems", "approval workflows", "role-based access control"],
        "related_assets_id": ["sistem kontrol akses", "sistem manajemen alur kerja", "alur kerja persetujuan", "kontrol akses berbasis peran"],
        "security_principles_en": ["separation of duties", "least privilege", "dual control", "conflict prevention"],
        "security_principles_id": ["pemisahan tugas", "hak istimewa minimum", "kontrol ganda", "pencegahan konflik"]
    },
    "A.5.4": {
        "keywords_en": ["management responsibility", "security leadership", "oversight", "management commitment", "security governance", "executive sponsorship", "leadership accountability"],
        "keywords_id": ["tanggung jawab manajemen", "kepemimpinan keamanan", "pengawasan", "komitmen manajemen", "tata kelola keamanan", "sponsorship eksekutif", "akuntabilitas kepemimpinan"],
        "audit_indicators_en": ["management not involved in security decisions", "no executive security sponsor", "security lacks management support", "no security budget allocation", "security not on board agenda", "lack of leadership oversight"],
        "audit_indicators_id": ["manajemen tidak terlibat dalam keputusan keamanan", "tidak ada sponsor keamanan eksekutif", "keamanan kurang dukungan manajemen", "tidak ada alokasi anggaran keamanan", "keamanan tidak dalam agenda dewan", "kurang pengawasan kepemimpinan"],
        "related_assets_en": ["governance committees", "security steering committee", "executive leadership", "board documentation"],
        "related_assets_id": ["komite tata kelola", "komite pengarah keamanan", "kepemimpinan eksekutif", "dokumentasi dewan"],
        "security_principles_en": ["management commitment", "governance oversight", "leadership accountability", "tone at the top"],
        "security_principles_id": ["komitmen manajemen", "pengawasan tata kelola", "akuntabilitas kepemimpinan", "nada dari atas"]
    },
    "A.5.5": {
        "keywords_en": ["authority contacts", "regulatory authorities", "law enforcement", "certification bodies", "regulatory compliance", "external authorities", "government agencies"],
        "keywords_id": ["kontak otoritas", "otoritas regulasi", "penegak hukum", "lembaga sertifikasi", "kepatuhan regulasi", "otoritas eksternal", "lembaga pemerintah"],
        "audit_indicators_en": ["no designated contact with authorities", "unclear reporting requirements", "no relationships with regulatory bodies", "failure to report incidents to authorities", "lack of authority communication channels"],
        "audit_indicators_id": ["tidak ada kontak yang ditunjuk dengan otoritas", "persyaratan pelaporan tidak jelas", "tidak ada hubungan dengan lembaga regulasi", "gagal melaporkan insiden ke otoritas", "kurang saluran komunikasi otoritas"],
        "related_assets_en": ["regulatory compliance documentation", "contact lists", "reporting procedures", "communication channels"],
        "related_assets_id": ["dokumentasi kepatuhan regulasi", "daftar kontak", "prosedur pelaporan", "saluran komunikasi"],
        "security_principles_en": ["regulatory compliance", "legal cooperation", "authority liaison", "incident reporting"],
        "security_principles_id": ["kepatuhan regulasi", "kerjasama hukum", "hubungan otoritas", "pelaporan insiden"]
    },
    "A.5.6": {
        "keywords_en": ["special interest groups", "security forums", "professional associations", "industry groups", " CERT", "CSIRT", "security communities", "information sharing"],
        "keywords_id": ["kelompok kepentingan khusus", "forum keamanan", "asosiasi profesional", "kelompok industri", "CERT", "CSIRT", "komunitas keamanan", "berbagi informasi"],
        "audit_indicators_en": ["no membership in security forums", "no threat intelligence sharing", "isolated from security community", "no participation in industry groups", "lack of external security networking"],
        "audit_indicators_id": ["tidak ada keanggotaan di forum keamanan", "tidak ada berbagi intelijen ancaman", "terisolasi dari komunitas keamanan", "tidak ada partisipasi dalam kelompok industri", "kurang jaringan keamanan eksternal"],
        "related_assets_en": ["forum memberships", "security mailing lists", "professional networks", "threat intelligence platforms"],
        "related_assets_id": ["keanggotaan forum", "milis keamanan", "jaringan profesional", "platform intelijen ancaman"],
        "security_principles_en": ["information sharing", "community collaboration", "collective defense", "threat intelligence"],
        "security_principles_id": ["berbagi informasi", "kolaborasi komunitas", "pertahanan kolektif", "intelijen ancaman"]
    },
    "A.5.7": {
        "keywords_en": ["threat intelligence", "threat landscape", "vulnerability intelligence", "threat feeds", "security monitoring", "threat analysis", "indicators of compromise", "APT tracking"],
        "keywords_id": ["intelijen ancaman", " Lanskap ancaman", "intelijen kerentanan", "feed ancaman", "pemantauan keamanan", "analisis ancaman", "indikator kompromi", "pelacakan APT"],
        "audit_indicators_en": ["no threat intelligence gathering", "unaware of emerging threats", "no vulnerability monitoring", "reactive security posture", "no threat analysis process", "blind to threat landscape"],
        "audit_indicators_id": ["tidak ada pengumpulan intelijen ancaman", "tidak aware terhadap ancaman yang muncul", "tidak ada pemantauan kerentanan", "postur keamanan reaktif", "tidak ada proses analisis ancaman", "buta terhadap lanskap ancaman"],
        "related_assets_en": ["threat intelligence platforms", "SIEM systems", "security information sources", "threat feeds"],
        "related_assets_id": ["platform intelijen ancaman", "sistem SIEM", "sumber informasi keamanan", "feed ancaman"],
        "security_principles_en": ["threat-aware security", "proactive defense", "intelligence-driven security", "situational awareness"],
        "security_principles_id": ["keamanan sadar ancaman", "pertahanan proaktif", "keamanan berbasis intelijen", "kesadaran situasional"]
    },
    "A.5.8": {
        "keywords_en": ["project management security", "secure development lifecycle", "security in projects", "project risk assessment", "security requirements", "project security controls"],
        "keywords_id": ["keamanan manajemen proyek", "siklus hidup pengembangan aman", "keamanan dalam proyek", "penilaian risiko proyek", "persyaratan keamanan", "kontrol keamanan proyek"],
        "audit_indicators_en": ["security not considered in projects", "no security requirements in project charters", "security bolted on after development", "no project risk assessments", "security ignored in project planning"],
        "audit_indicators_id": ["keamanan tidak dipertimbangkan dalam proyek", "tidak ada persyaratan keamanan dalam piagam proyek", "keamanan ditambahkan setelah pengembangan", "tidak ada penilaian risiko proyek", "keamanan diabaikan dalam perencanaan proyek"],
        "related_assets_en": ["project management tools", "development methodologies", "security requirements documentation", "project charters"],
        "related_assets_id": ["alat manajemen proyek", "metodologi pengembangan", "dokumentasi persyaratan keamanan", "piagam proyek"],
        "security_principles_en": ["security by design", "secure development", "risk-based projects", "integrated security"],
        "security_principles_id": ["keamanan sejak desain", "pengembangan aman", "proyek berbasis risiko", "keamanan terintegrasi"]
    },
    "A.5.9": {
        "keywords_en": ["asset inventory", "information assets", "asset classification", "asset register", "hardware inventory", "software inventory", "data inventory", "asset management"],
        "keywords_id": ["inventarisasi aset", "aset informasi", "klasifikasi aset", "register aset", "inventaris perangkat keras", "inventaris perangkat lunak", "inventaris data", "manajemen aset"],
        "audit_indicators_en": ["no asset inventory exists", "unauthorized assets on network", "inventory incomplete", "shadow IT undiscovered", "unknown devices", "rogue systems", "asset tracking failures"],
        "audit_indicators_id": ["tidak ada inventaris aset", "aset tidak berwenang di jaringan", "inventaris tidak lengkap", "shadow IT tidak terdeteksi", "perangkat tidak dikenal", "sistem nakal", "kegagalan pelacakan aset"],
        "related_assets_en": ["asset management systems", "CMDB", "discovery tools", "inventory databases"],
        "related_assets_id": ["sistem manajemen aset", "CMDB", "alat penemuan", "database inventaris"],
        "security_principles_en": ["asset management", "visibility", "accountability", "asset governance"],
        "security_principles_id": ["manajemen aset", "visibilitas", "akuntabilitas", "tata kelola aset"]
    },
    "A.5.10": {
        "keywords_en": ["acceptable use policy", "AUP", "usage guidelines", "resource usage", "acceptable use", "user conduct", "email policy", "internet usage policy"],
        "keywords_id": ["kebijakan penggunaan yang dapat diterima", "AUP", "pedoman penggunaan", "penggunaan sumber daya", "penggunaan yang dapat diterima", "perilaku pengguna", "kebijakan email", "kebijakan penggunaan internet"],
        "audit_indicators_en": ["no acceptable use policy", "users violate usage policies", "no policy acknowledgment signed", "unauthorized software usage", "excessive personal use", "policy not enforced"],
        "audit_indicators_id": ["tidak ada kebijakan penggunaan", "pengguna melanggar kebijakan penggunaan", "tidak ada tanda tangan pengakuan kebijakan", "penggunaan perangkat lunak tidak berwenang", "penggunaan pribadi berlebihan", "kebijakan tidak ditegakkan"],
        "related_assets_en": ["policy documents", "user agreements", "monitoring systems", "proxy servers"],
        "related_assets_id": ["dokumen kebijakan", "perjanjian pengguna", "sistem pemantauan", "server proxy"],
        "security_principles_en": ["acceptable use", "policy compliance", "user responsibility", "resource protection"],
        "security_principles_id": ["penggunaan yang dapat diterima", "kepatuhan kebijakan", "tanggung jawab pengguna", "perlindungan sumber daya"]
    },
    "A.5.11": {
        "keywords_en": ["asset return", "employee termination", "offboarding", "asset recovery", "equipment return", "data handover", "exit procedures"],
        "keywords_id": ["pengembalian aset", "pemberhentian karyawan", "offboarding", "pemulihan aset", "pengembalian peralatan", "serah terima data", "prosedur keluar"],
        "audit_indicators_en": ["assets not returned upon termination", "missing equipment after employee leaves", "no asset return process", "data not recovered", "accounts not disabled", "access not revoked"],
        "audit_indicators_id": ["aset tidak dikembalikan saat pemberhentian", "peralatan hilang setelah karyawan keluar", "tidak ada proses pengembalian aset", "data tidak dipulihkan", "akun tidak dinonaktifkan", "akses tidak dicabut"],
        "related_assets_en": ["HR systems", "asset tracking", "access control systems", "offboarding checklists"],
        "related_assets_id": ["sistem HR", "pelacakan aset", "sistem kontrol akses", "daftar periksa offboarding"],
        "security_principles_en": ["access revocation", "asset recovery", "termination procedures", "accountability"],
        "security_principles_id": ["pencabutan akses", "pemulihan aset", "prosedur pemberhentian", "akuntabilitas"]
    },
    "A.5.12": {
        "keywords_en": ["information classification", "data classification", "sensitivity levels", "classification scheme", "confidentiality labeling", "public private confidential", "data categorization"],
        "keywords_id": ["klasifikasi informasi", "klasifikasi data", "tingkat sensitivitas", "skema klasifikasi", "pelabelan kerahasiaan", "publik privat rahasia", "kategorisasi data"],
        "audit_indicators_en": ["no classification scheme", "all data treated equally", "sensitive data unprotected", "over-classification", "under-classification", "no classification procedures"],
        "audit_indicators_id": ["tidak ada skema klasifikasi", "semua data diperlakukan sama", "data sensitif tidak dilindungi", "over-klasifikasi", "under-klasifikasi", "tidak ada prosedur klasifikasi"],
        "related_assets_en": ["classification policies", "data handling procedures", "labeling systems", "DLP systems"],
        "related_assets_id": ["kebijakan klasifikasi", "prosedur penanganan data", "sistem pelabelan", "sistem DLP"],
        "security_principles_en": ["need to know", "data protection", "classification-based protection", "sensitivity management"],
        "security_principles_id": ["perlu diketahui", "perlindungan data", "perlindungan berbasis klasifikasi", "manajemen sensitivitas"]
    },
    "A.5.13": {
        "keywords_en": ["information labeling", "data labeling", "classification labels", "document marking", "header footer labeling", "sensitivity labels", "visual indicators"],
        "keywords_id": ["pelabelan informasi", "pelabelan data", "label klasifikasi", "penandaan dokumen", "pelabelan header footer", "label sensitivitas", "indikator visual"],
        "audit_indicators_en": ["documents not labeled", "labels missing", "incorrect labels applied", "no label enforcement", "labels ignored", "inconsistent labeling"],
        "audit_indicators_id": ["dokumen tidak berlabel", "label hilang", "label yang salah diterapkan", "tidak ada penegakan label", "label diabaikan", "pelabelan tidak konsisten"],
        "related_assets_en": ["document management systems", "email systems", "labeling tools", "DLP solutions"],
        "related_assets_id": ["sistem manajemen dokumen", "sistem email", "alat pelabelan", "solusi DLP"],
        "security_principles_en": ["visual security indicators", "classification enforcement", "user awareness", "handling guidance"],
        "security_principles_id": ["indikator keamanan visual", "penegakan klasifikasi", "kesadaran pengguna", "panduan penanganan"]
    },
    "A.5.14": {
        "keywords_en": ["information transfer", "data transfer", "file transfer", "cross-border transfer", "data transmission", "secure transfer protocols", "transfer controls"],
        "keywords_id": ["transfer informasi", "transfer data", "transfer file", "transfer lintas batas", "transmisi data", "protokol transfer aman", "kontrol transfer"],
        "audit_indicators_en": ["unencrypted data transfers", "unauthorized transfers", "no transfer logging", "insecure protocols used", "cross-border compliance issues", "transfer controls bypassed"],
        "audit_indicators_id": ["transfer data tidak terenkripsi", "transfer tidak berwenang", "tidak ada logging transfer", "protokol tidak aman digunakan", "masalah kepatuhan lintas batas", "kontrol transfer dilewati"],
        "related_assets_en": ["file transfer systems", "encryption tools", "network monitoring", "transfer logs"],
        "related_assets_id": ["sistem transfer file", "alat enkripsi", "pemantauan jaringan", "log transfer"],
        "security_principles_en": ["secure transmission", "data in transit protection", "transfer authorization", "compliance"],
        "security_principles_id": ["transmisi aman", "perlindungan data dalam perjalanan", "otorisasi transfer", "kepatuhan"]
    },
    "A.5.15": {
        "keywords_en": ["access control", "authentication", "authorization", "access control policy", "logical access", "physical access", "access denial"],
        "keywords_id": ["kontrol akses", "autentikasi", "otorisasi", "kebijakan kontrol akses", "akses logis", "akses fisik", "penolakan akses"],
        "audit_indicators_en": ["excessive access rights", "no access review process", "default passwords unchanged", "shared accounts", "unterminated access", "access not principle of least privilege"],
        "audit_indicators_id": ["hak akses berlebihan", "tidak ada proses tinjauan akses", "kata sandi default tidak diubah", "akun bersama", "akses tidak diakhiri", "akses tidak sesuai hak istimewa minimum"],
        "related_assets_en": ["access control systems", "authentication servers", "directory services", "privileged access management"],
        "related_assets_id": ["sistem kontrol akses", "server autentikasi", "layanan direktori", "manajemen akses istimewa"],
        "security_principles_en": ["least privilege", "need to know", "access denial", "accountability"],
        "security_principles_id": ["hak istimewa minimum", "perlu diketahui", "penolakan akses", "akuntabilitas"]
    },
    "A.5.16": {
        "keywords_en": ["identity management", "user lifecycle", "provisioning", "deprovisioning", "identity lifecycle", "user accounts", "authentication credentials"],
        "keywords_id": ["manajemen identitas", "siklus hidup pengguna", "provisioning", "deprovisioning", "siklus hidup identitas", "akun pengguna", "kredensial autentikasi"],
        "audit_indicators_en": ["orphaned accounts", "no user provisioning process", "accounts not disabled on termination", "excessive privileges", "no identity verification", "inconsistent identity management"],
        "audit_indicators_id": ["akun yatim", "tidak ada proses provisioning pengguna", "akun tidak dinonaktifkan saat pemberhentian", "hak istimewa berlebihan", "tidak ada verifikasi identitas", "manajemen identitas tidak konsisten"],
        "related_assets_en": ["identity management systems", "HR systems", "provisioning workflows", "directory services"],
        "related_assets_id": ["sistem manajemen identitas", "sistem HR", "alur kerja provisioning", "layanan direktori"],
        "security_principles_en": ["identity assurance", "lifecycle management", "provisioning controls", "identity verification"],
        "security_principles_id": ["jaminan identitas", "manajemen siklus hidup", "kontrol provisioning", "verifikasi identitas"]
    },
    "A.5.17": {
        "keywords_en": ["authentication information", "passwords", "MFA", "multi-factor authentication", "credentials", "authentication tokens", "biometrics", "smart cards"],
        "keywords_id": ["informasi autentikasi", "kata sandi", "MFA", "autentikasi multi-faktor", "kredensial", "token autentikasi", "biometrik", "kartu pintar"],
        "audit_indicators_en": ["weak passwords", "no MFA implemented", "password sharing", "default passwords", "credentials transmitted insecurely", "no password complexity", "authentication bypass"],
        "audit_indicators_id": ["kata sandi lemah", "MFA tidak diimplementasikan", "berbagi kata sandi", "kata sandi default", "kredensial dikirim tidak aman", "tidak ada kompleksitas kata sandi", "pemindaian autentikasi"],
        "related_assets_en": ["authentication servers", "MFA systems", "password management tools", "biometric devices"],
        "related_assets_id": ["server autentikasi", "sistem MFA", "alat manajemen kata sandi", "perangkat biometrik"],
        "security_principles_en": ["strong authentication", "multi-factor", "credential protection", "identity verification"],
        "security_principles_id": ["autentikasi kuat", "multi-faktor", "perlindungan kredensial", "verifikasi identitas"]
    },
    "A.5.18": {
        "keywords_en": ["access rights", "privilege management", "authorization", "access permissions", "privilege assignment", "role-based access", "access approval"],
        "keywords_id": ["hak akses", "manajemen hak istimewa", "otorisasi", "izin akses", "penugasan hak istimewa", "akses berbasis peran", "persetujuan akses"],
        "audit_indicators_en": ["excessive privileges", "no periodic access review", "unauthorized access granted", "privilege creep", "segregation of duties violations", "access not documented"],
        "audit_indicators_id": ["hak istimewa berlebihan", "tidak ada tinjauan akses berkala", "akses tidak berwenang diberikan", "hak istimewa merayap", "pelanggaran pemisahan tugas", "akses tidak didokumentasikan"],
        "related_assets_en": ["access control systems", "entitlement management", "approval workflows", "access logs"],
        "related_assets_id": ["sistem kontrol akses", "manajemen hak", "alur kerja persetujuan", "log akses"],
        "security_principles_en": ["least privilege", "access review", "privilege segregation", "access governance"],
        "security_principles_id": ["hak istimewa minimum", "tinjauan akses", "segregasi hak istimewa", "tata kelola akses"]
    },
    "A.5.19": {
        "keywords_en": ["supplier security", "vendor management", "third-party risk", "supply chain security", "vendor agreements", "outsourcing security"],
        "keywords_id": ["keamanan pemasok", "manajemen vendor", "risiko pihak ketiga", "keamanan rantai pasok", "perjanjian vendor", "keamanan outsourcing"],
        "audit_indicators_en": ["no supplier security assessment", "vendors without security clauses", "untrusted third-party access", "supplier security not monitored", "no vendor risk management"],
        "audit_indicators_id": ["tidak ada penilaian keamanan pemasok", "vendor tanpa klausa keamanan", "akses pihak ketiga tidak dipercaya", "keamanan pemasok tidak dipantau", "tidak ada manajemen risiko vendor"],
        "related_assets_en": ["vendor portals", "third-party systems", "supply chain platforms", "vendor contracts"],
        "related_assets_id": ["portal vendor", "sistem pihak ketiga", "platform rantai pasok", "kontrak vendor"],
        "security_principles_en": ["supply chain risk", "vendor governance", "third-party assurance", "outsourced security"],
        "security_principles_id": ["risiko rantai pasok", "tata kelola vendor", "jaminan pihak ketiga", "keamanan outsourcing"]
    },
    "A.5.20": {
        "keywords_en": ["supplier agreements", "vendor contracts", "security clauses", "SLA", "service level agreements", "contractual security", "third-party contracts"],
        "keywords_id": ["perjanjian pemasok", "kontrak vendor", "klausa keamanan", "SLA", "perjanjian tingkat layanan", "keamanan kontraktual", "kontrak pihak ketiga"],
        "audit_indicators_en": ["contracts lack security requirements", "no security SLA", "vendor obligations undefined", "no incident response clauses", "weak security terms"],
        "audit_indicators_id": ["kontrak kurang persyaratan keamanan", "tidak ada SLA keamanan", "kewajiban vendor tidak didefinisikan", "tidak ada klausa respons insiden", "ketentuan keamanan lemah"],
        "related_assets_en": ["contract management systems", "legal documentation", "vendor agreements"],
        "related_assets_id": ["sistem manajemen kontrak", "dokumentasi hukum", "perjanjian vendor"],
        "security_principles_en": ["contractual security", "vendor obligations", "SLA enforcement", "legal compliance"],
        "security_principles_id": ["keamanan kontraktual", "kewajiban vendor", "penegakan SLA", "kepatuhan hukum"]
    },
    "A.5.21": {
        "keywords_en": ["ICT supply chain", "vendor risk management", "software supply chain", "hardware supply chain", "supplier continuity", "ICT security in supply chain"],
        "keywords_id": ["rantai pasok TIK", "manajemen risiko vendor", "rantai pasok perangkat lunak", "rantai pasok perangkat keras", "kelangsungan pemasok", "keamanan TIK dalam rantai pasok"],
        "audit_indicators_en": ["no supply chain risk assessment", "unknown software sources", "unverified hardware suppliers", "no supplier continuity planning", "supply chain attacks not considered"],
        "audit_indicators_id": ["tidak ada penilaian risiko rantai pasok", "sumber perangkat lunak tidak diketahui", "pemasok perangkat keras tidak diverifikasi", "tidak ada perencanaan kelangsungan pemasok", "serangan rantai pasok tidak dipertimbangkan"],
        "related_assets_en": ["supply chain management tools", "software repositories", "hardware inventories", "vendor databases"],
        "related_assets_id": ["alat manajemen rantai pasok", "repositori perangkat lunak", "inventaris perangkat keras", "database vendor"],
        "security_principles_en": ["supply chain integrity", "vendor trust", "provenance verification", "risk management"],
        "security_principles_id": ["integritas rantai pasok", "kepercayaan vendor", "verifikasi asal usul", "manajemen risiko"]
    },
    "A.5.22": {
        "keywords_en": ["supplier monitoring", "vendor performance", "service review", "change management", "supplier relationship management", "vendor oversight"],
        "keywords_id": ["pemantauan pemasok", "kinerja vendor", "tinjauan layanan", "manajemen perubahan", "manajemen hubungan pemasok", "pengawasan vendor"],
        "audit_indicators_en": ["no supplier monitoring", "vendor changes uncontrolled", "service degradation undetected", "no performance reviews", "supplier issues unaddressed"],
        "audit_indicators_id": ["tidak ada pemantauan pemasok", "perubahan vendor tidak terkendali", "degradasi layanan tidak terdeteksi", "tidak ada tinjauan kinerja", "masalah pemasok tidak diatasi"],
        "related_assets_en": ["monitoring systems", "performance dashboards", "change management tools", "vendor portals"],
        "related_assets_id": ["sistem pemantauan", "dashboard kinerja", "alat manajemen perubahan", "portal vendor"],
        "security_principles_en": ["continuous monitoring", "vendor oversight", "change control", "performance management"],
        "security_principles_id": ["pemantauan berkelanjutan", "pengawasan vendor", "kontrol perubahan", "manajemen kinerja"]
    },
    "A.5.23": {
        "keywords_en": ["cloud security", "IaaS", "PaaS", "SaaS", "cloud service provider", "shared responsibility", "cloud governance"],
        "keywords_id": ["keamanan cloud", "IaaS", "PaaS", "SaaS", "penyedia layanan cloud", "tanggung jawab bersama", "tata kelola cloud"],
        "audit_indicators_en": ["unclear cloud responsibilities", "data exposed in cloud", "no cloud security assessment", "misconfigured cloud services", "shadow cloud usage"],
        "audit_indicators_id": ["tanggung jawab cloud tidak jelas", "data terekspos di cloud", "tidak ada penilaian keamanan cloud", "layanan cloud salah konfigurasi", "penggunaan cloud bayangan"],
        "related_assets_en": ["cloud platforms", "cloud security tools", "IAM systems", "encryption services"],
        "related_assets_id": ["platform cloud", "alat keamanan cloud", "sistem IAM", "layanan enkripsi"],
        "security_principles_en": ["shared responsibility model", "cloud-native security", "data protection in cloud", "compliance in cloud"],
        "security_principles_id": ["model tanggung jawab bersama", "keamanan cloud-native", "perlindungan data di cloud", "kepatuhan di cloud"]
    },
    "A.5.24": {
        "keywords_en": ["incident management planning", "incident response plan", "IR plan", "emergency preparedness", "incident procedures", "crisis management"],
        "keywords_id": ["perencanaan manajemen insiden", "rencana respons insiden", "rencana RI", "kesiapan darurat", "prosedur insiden", "manajemen krisis"],
        "audit_indicators_en": ["no incident response plan", "plan not tested", "roles undefined", "no communication procedures", "incomplete plan", "plan not updated"],
        "audit_indicators_id": ["tidak ada rencana respons insiden", "rencana tidak diuji", "peran tidak didefinisikan", "tidak ada prosedur komunikasi", "rencana tidak lengkap", "rencana tidak diperbarui"],
        "related_assets_en": ["incident response plans", "emergency procedures", "communication systems", "crisis management tools"],
        "related_assets_id": ["rencana respons insiden", "prosedur darurat", "sistem komunikasi", "alat manajemen krisis"],
        "security_principles_en": ["preparedness", "incident response", "crisis management", "business continuity"],
        "security_principles_id": ["kesiapan", "respons insiden", "manajemen krisis", "kelangsungan bisnis"]
    },
    "A.5.25": {
        "keywords_en": ["incident assessment", "incident classification", "event triage", "security incident evaluation", "incident prioritization", "damage assessment"],
        "keywords_id": ["penilaian insiden", "klasifikasi insiden", "triase peristiwa", "evaluasi insiden keamanan", "prioritisasi insiden", "penilaian kerusakan"],
        "audit_indicators_en": ["no incident classification process", "incidents not assessed properly", "delayed incident response", "incorrect incident categorization", "no triage procedures"],
        "audit_indicators_id": ["tidak ada proses klasifikasi insiden", "insiden tidak dinilai dengan benar", "respons insiden tertunda", "kategorisasi insiden tidak benar", "tidak ada prosedur triase"],
        "related_assets_en": ["incident tracking systems", "ticketing systems", "assessment tools", "classification matrices"],
        "related_assets_id": ["sistem pelacakan insiden", "sistem tiket", "alat penilaian", "matriks klasifikasi"],
        "security_principles_en": ["incident prioritization", "risk-based response", "triage", "impact assessment"],
        "security_principles_id": ["prioritisasi insiden", "respons berbasis risiko", "triase", "penilaian dampak"]
    },
    "A.5.26": {
        "keywords_en": ["incident response", "containment", "eradication", "recovery", "incident handling", "IR procedures", "forensic response"],
        "keywords_id": ["respons insiden", "penahanan", "pemberantasan", "pemulihan", "penanganan insiden", "prosedur RI", "respons forensik"],
        "audit_indicators_en": ["slow incident response", "containment failures", "inadequate recovery", "no documentation of response", "lessons not learned", "recurrence of incidents"],
        "audit_indicators_id": ["respons insiden lambat", "kegagalan penahanan", "pemulihan tidak memadai", "tidak ada dokumentasi respons", "pelajaran tidak dipelajari", "kejadian berulang"],
        "related_assets_en": ["incident response tools", "forensic toolkits", "backup systems", "communication platforms"],
        "related_assets_id": ["alat respons insiden", "toolkit forensik", "sistem cadangan", "platform komunikasi"],
        "security_principles_en": ["rapid response", "containment first", "evidence preservation", "business recovery"],
        "security_principles_id": ["respons cepat", "penahanan dulu", "pelestarian bukti", "pemulihan bisnis"]
    },
    "A.5.27": {
        "keywords_en": ["incident post-mortem", "lessons learned", "incident review", "knowledge management", "incident debrief", "after-action review"],
        "keywords_id": ["pasca-insiden", "pelajaran dipelajari", "tinjauan insiden", "manajemen pengetahuan", "debriefing insiden", "tinjauan tindak lanjut"],
        "audit_indicators_en": ["no post-incident reviews", "recurring incidents", "lessons not documented", "no knowledge sharing", "same mistakes repeated"],
        "audit_indicators_id": ["tidak ada tinjauan pasca-insiden", "insiden berulang", "pelajaran tidak didokumentasikan", "tidak ada berbagi pengetahuan", "kesalahan yang sama diulang"],
        "related_assets_en": ["knowledge bases", "incident databases", "training materials", "review reports"],
        "related_assets_id": ["basis pengetahuan", "database insiden", "materi pelatihan", "laporan tinjauan"],
        "security_principles_en": ["continuous improvement", "knowledge management", "organizational learning", "preventive action"],
        "security_principles_id": ["perbaikan berkelanjutan", "manajemen pengetahuan", "pembelajaran organisasi", "tindakan pencegahan"]
    },
    "A.5.28": {
        "keywords_en": ["evidence collection", "digital forensics", "chain of custody", "evidence preservation", "forensic investigation", "legal evidence"],
        "keywords_id": ["pengumpulan bukti", "forensik digital", "rantai penahanan", "pelestarian bukti", "investigasi forensik", "bukti hukum"],
        "audit_indicators_en": ["evidence not preserved", "chain of custody broken", "forensic procedures not followed", "evidence contaminated", "no evidence collection process"],
        "audit_indicators_id": ["bukti tidak dilestarikan", "rantai penahanan putus", "prosedur forensik tidak diikuti", "bukti terkontaminasi", "tidak ada proses pengumpulan bukti"],
        "related_assets_en": ["forensic toolkits", "evidence storage", "imaging tools", "logging systems"],
        "related_assets_id": ["toolkit forensik", "penyimpanan bukti", "alat imaging", "sistem logging"],
        "security_principles_en": ["evidence integrity", "chain of custody", "forensic soundness", "legal admissibility"],
        "security_principles_id": ["integritas bukti", "rantai penahanan", "kelayakan forensik", "keterterimaan hukum"]
    },
    "A.5.29": {
        "keywords_en": ["information security during disruption", "disaster recovery", "business continuity", "crisis procedures", "disruption response"],
        "keywords_id": ["keamanan informasi selama gangguan", "pemulihan bencana", "kelangsungan bisnis", "prosedur krisis", "respons gangguan"],
        "audit_indicators_en": ["security compromised during incidents", "no continuity plans", "critical functions not protected", "communication failures", "inadequate disaster recovery"],
        "audit_indicators_id": ["keamanan dikompromikan selama insiden", "tidak ada rencana kelangsungan", "fungsi kritis tidak dilindungi", "kegagalan komunikasi", "pemulihan bencana tidak memadai"],
        "related_assets_en": ["business continuity plans", "DR sites", "backup systems", "emergency communication"],
        "related_assets_id": ["rencana kelangsungan bisnis", "situs DR", "sistem cadangan", "komunikasi darurat"],
        "security_principles_en": ["resilience", "business continuity", "disaster recovery", "crisis management"],
        "security_principles_id": ["ketahanan", "kelangsungan bisnis", "pemulihan bencana", "manajemen krisis"]
    },
    "A.5.30": {
        "keywords_en": ["ICT readiness", "system availability", "recovery capability", "backup systems", "high availability", "disaster recovery testing"],
        "keywords_id": ["kesiapan TIK", "ketersediaan sistem", "kapabilitas pemulihan", "sistem cadangan", "ketersediaan tinggi", "pengujian pemulihan bencana"],
        "audit_indicators_en": ["untested backup systems", "no recovery time objectives", "systems not recoverable", "backup failures", "no high availability"],
        "audit_indicators_id": ["sistem cadangan tidak diuji", "tidak ada tujuan waktu pemulihan", "sistem tidak dapat dipulihkan", "kegagalan cadangan", "tidak ada ketersediaan tinggi"],
        "related_assets_en": ["backup systems", "recovery sites", "high availability clusters", "load balancers"],
        "related_assets_id": ["sistem cadangan", "situs pemulihan", "cluster ketersediaan tinggi", "penyeimbang beban"],
        "security_principles_en": ["availability", "recoverability", "redundancy", "resilience"],
        "security_principles_id": ["ketersediaan", "dapat dipulihkan", "redundansi", "ketahanan"]
    },
    "A.5.31": {
        "keywords_en": ["legal requirements", "regulatory compliance", "statutory obligations", "data protection laws", "industry regulations", "compliance monitoring"],
        "keywords_id": ["persyaratan hukum", "kepatuhan regulasi", "kewajiban statuta", "hukum perlindungan data", "regulasi industri", "pemantauan kepatuhan"],
        "audit_indicators_en": ["non-compliance with regulations", "legal requirements not identified", "no compliance monitoring", "regulatory fines", "violations of data protection laws"],
        "audit_indicators_id": ["ketidakpatuhan terhadap regulasi", "persyaratan hukum tidak diidentifikasi", "tidak ada pemantauan kepatuhan", "denda regulasi", "pelanggaran hukum perlindungan data"],
        "related_assets_en": ["compliance management systems", "legal documentation", "regulatory update services"],
        "related_assets_id": ["sistem manajemen kepatuhan", "dokumentasi hukum", "layanan pembaruan regulasi"],
        "security_principles_en": ["legal compliance", "regulatory adherence", "data protection", "privacy rights"],
        "security_principles_id": ["kepatuhan hukum", "kepatuhan regulasi", "perlindungan data", "hak privasi"]
    },
    "A.5.32": {
        "keywords_en": ["intellectual property protection", "IP rights", "copyright", "trademarks", "trade secrets", "software licensing", "IP compliance"],
        "keywords_id": ["perlindungan kekayaan intelektual", "hak KI", "hak cipta", "merek dagang", "rahasia dagang", "lisensi perangkat lunak", "kepatuhan KI"],
        "audit_indicators_en": ["unlicensed software", "IP violations", "copyright infringement", "trade secrets unprotected", "software license compliance issues"],
        "audit_indicators_id": ["perangkat lunak tidak berlisensi", "pelanggaran KI", "pelanggaran hak cipta", "rahasia dagang tidak dilindungi", "masalah kepatuhan lisensi perangkat lunak"],
        "related_assets_en": ["software assets", "license management tools", "IP documentation"],
        "related_assets_id": ["aset perangkat lunak", "alat manajemen lisensi", "dokumentasi KI"],
        "security_principles_en": ["IP protection", "license compliance", "intellectual property rights", "legal protection"],
        "security_principles_id": ["perlindungan KI", "kepatuhan lisensi", "hak kekayaan intelektual", "perlindungan hukum"]
    },
    "A.5.33": {
        "keywords_en": ["record protection", "data retention", "record retention", "archiving", "disposal procedures", "record lifecycle"],
        "keywords_id": ["perlindungan catatan", "retensi data", "retensi catatan", "pengarsipan", "prosedur pembuangan", "siklus hidup catatan"],
        "audit_indicators_en": ["records not retained properly", "disposal procedures not followed", "inadequate archiving", "records lost", "unauthorized destruction of records"],
        "audit_indicators_id": ["catatan tidak dipertahankan dengan benar", "prosedur pembuangan tidak diikuti", "pengarsipan tidak memadai", "catatan hilang", "penghancuran catatan tidak berwenang"],
        "related_assets_en": ["archiving systems", "records management", "backup media", "disposal services"],
        "related_assets_id": ["sistem pengarsipan", "manajemen catatan", "media cadangan", "layanan pembuangan"],
        "security_principles_en": ["data retention", "records management", "secure disposal", "lifecycle management"],
        "security_principles_id": ["retensi data", "manajemen catatan", "pembuangan aman", "manajemen siklus hidup"]
    },
    "A.5.34": {
        "keywords_en": ["privacy", "data privacy", "privacy protection", "personal data", "GDPR", "privacy rights", "consent management"],
        "keywords_id": ["privasi", "privasi data", "perlindungan privasi", "data pribadi", "GDPR", "hak privasi", "manajemen persetujuan"],
        "audit_indicators_en": ["privacy violations", "inadequate consent", "personal data exposed", "privacy policies not followed", "GDPR non-compliance"],
        "audit_indicators_id": ["pelanggaran privasi", "persetujuan tidak memadai", "data pribadi terekspos", "kebijakan privasi tidak diikuti", "ketidakpatuhan GDPR"],
        "related_assets_en": ["personal data systems", "consent management platforms", "privacy impact assessment tools"],
        "related_assets_id": ["sistem data pribadi", "platform manajemen persetujuan", "alat penilaian dampak privasi"],
        "security_principles_en": ["privacy by design", "data minimization", "consent management", "privacy rights"],
        "security_principles_id": ["privasi sejak desain", "minimisasi data", "manajemen persetujuan", "hak privasi"]
    },
    "A.5.35": {
        "keywords_en": ["independent review", "security audit", "internal audit", "external audit", "compliance review", "security assessment"],
        "keywords_id": ["tinjauan independen", "audit keamanan", "audit internal", "audit eksternal", "tinjauan kepatuhan", "penilaian keamanan"],
        "audit_indicators_en": ["no security audits conducted", "audit recommendations ignored", "inadequate audit coverage", "no independent review", "audit findings not addressed"],
        "audit_indicators_id": ["tidak ada audit keamanan", "rekomendasi audit diabaikan", "cakupan audit tidak memadai", "tidak ada tinjauan independen", "temuan audit tidak diatasi"],
        "related_assets_en": ["audit management systems", "compliance tools", "risk assessment platforms"],
        "related_assets_id": ["sistem manajemen audit", "alat kepatuhan", "platform penilaian risiko"],
        "security_principles_en": ["independent oversight", "audit compliance", "continuous improvement", "accountability"],
        "security_principles_id": ["pengawasan independen", "kepatuhan audit", "perbaikan berkelanjutan", "akuntabilitas"]
    },
    "A.5.36": {
        "keywords_en": ["compliance with policies", "policy compliance", "technical compliance", "policy adherence", "security standards", "technical controls"],
        "keywords_id": ["kepatuhan terhadap kebijakan", "kepatuhan kebijakan", "kepatuhan teknis", "kepatuhan kebijakan", "standar keamanan", "kontrol teknis"],
        "audit_indicators_en": ["policies not followed", "technical controls ineffective", "standards not met", "non-compliant configurations", "policy violations undetected"],
        "audit_indicators_id": ["kebijakan tidak diikuti", "kontrol teknis tidak efektif", "standar tidak terpenuhi", "konfigurasi tidak patuh", "pelanggaran kebijakan tidak terdeteksi"],
        "related_assets_en": ["compliance monitoring tools", "policy management systems", "technical controls"],
        "related_assets_id": ["alat pemantauan kepatuhan", "sistem manajemen kebijakan", "kontrol teknis"],
        "security_principles_en": ["policy enforcement", "technical compliance", "standards adherence", "control effectiveness"],
        "security_principles_id": ["penegakan kebijakan", "kepatuhan teknis", "kepatuhan standar", "efektivitas kontrol"]
    },
    "A.5.37": {
        "keywords_en": ["documented procedures", "security procedures", "operational procedures", "documentation standards", "procedure maintenance"],
        "keywords_id": ["prosedur yang didokumentasikan", "prosedur keamanan", "prosedur operasional", "standar dokumentasi", "pemeliharaan prosedur"],
        "audit_indicators_en": ["procedures not documented", "outdated procedures", "procedures not followed", "inconsistent documentation", "no procedure version control"],
        "audit_indicators_id": ["prosedur tidak didokumentasikan", "prosedur usang", "prosedur tidak diikuti", "dokumentasi tidak konsisten", "tidak ada kontrol versi prosedur"],
        "related_assets_en": ["procedure repositories", "document management systems", "knowledge bases"],
        "related_assets_id": ["repositori prosedur", "sistem manajemen dokumen", "basis pengetahuan"],
        "security_principles_en": ["process standardization", "documentation completeness", "procedure currency", "operational consistency"],
        "security_principles_id": ["standardisasi proses", "kelengkapan dokumentasi", "mata uang prosedur", "konsistensi operasional"]
    }
}

# Add enrichments to controls
enriched_controls = []
for control in controls:
    control_id = control["control_id"]
    if control_id in enrichments:
        control.update(enrichments[control_id])
    else:
        # Add empty fields if no enrichment defined
        control.update({
            "keywords_en": [], "keywords_id": [],
            "audit_indicators_en": [], "audit_indicators_id": [],
            "related_assets_en": [], "related_assets_id": [],
            "security_principles_en": [], "security_principles_id": []
        })
    enriched_controls.append(control)

# Save enriched controls
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(enriched_controls, f, indent=2, ensure_ascii=False)

print(f"Enriched {len(enriched_controls)} controls")
print(f"Output saved to: D:\\Hilmi\\Coding\\MasterFolderSkripsi\\RAG\\ragV1\\data\\iso_controls_enriched.json")
