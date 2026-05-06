import json

# Read the enriched controls
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    controls = json.load(f)

# Comprehensive enrichments for A.7 controls (Physical Security)
enrichments = {
    "A.7.1": {
        "keywords_en": ["physical security perimeter", "facility access control", "security zones", "perimeter protection", "access points", "security barriers", "physical entry control", "facility boundaries", "unauthorized access prevention", "secure areas"],
        "keywords_id": ["perimeter keamanan fisik", "kontrol akses fasilitas", "zona keamanan", "perlindungan perimeter", "titik akses", "penghalang keamanan", "kontrol masuk fisik", "batas fasilitas", "pencegahan akses tidak sah", "area aman"],
        "audit_indicators_en": ["no physical security perimeter defined", "perimeter barriers missing or damaged", "unrestricted access to facility", "security zones not marked", "access points unmonitored", "no visitor control procedures", "perimeter breach incidents", "lack of physical security barriers"],
        "audit_indicators_id": ["tidak ada perimeter keamanan fisik", "penghalang perimeter hilang atau rusak", "akses tidak terbatas ke fasilitas", "zona keamanan tidak ditandai", "titik akses tidak dipantau", "tidak ada prosedur kontrol pengunjung", "insiden pelanggaran perimeter", "kurangnya penghalang keamanan fisik"],
        "related_assets_en": ["facility perimeter", "security fences", "access gates", "security checkpoints", "CCTV cameras", "security lighting", "perimeter walls", "barrier gates", "guard posts", "vehicle barriers"],
        "related_assets_id": ["perimeter fasilitas", "pagar keamanan", "gerbang akses", "pos pemeriksaan keamanan", "kamera CCTV", "pencahayaan keamanan", "dinding perimeter", "gerbang penghalang", "pos penjagaan", "penghalang kendaraan"],
        "security_principles_en": ["defense in depth", "physical security", "access control", "deterrence", "delay", "detection"],
        "security_principles_id": ["pertahanan berlapis", "keamanan fisik", "kontrol akses", "pencegahan", "penundaan", "deteksi"]
    },
    "A.7.2": {
        "keywords_en": ["physical entry control", "access control systems", "visitor management", "badge system", "authentication factors", "entry logs", "access cards", "biometric authentication", "visitor badges", "secure entry"],
        "keywords_id": ["kontrol masuk fisik", "sistem kontrol akses", "manajemen pengunjung", "sistem lencana", "faktor autentikasi", "log masuk", "kartu akses", "autentikasi biometrik", "lencana pengunjung", "masuk aman"],
        "audit_indicators_en": ["no access control system", "uncontrolled access to secure areas", "visitor access not logged", "access cards not returned", "no authentication required", "tailgating incidents", "access credentials shared", "entry points not monitored"],
        "audit_indicators_id": ["tidak ada sistem kontrol akses", "akses tidak terkontrol ke area aman", "akses pengunjung tidak dicatat", "kartu akses tidak dikembalikan", "tidak ada autentikasi yang diperlukan", "insiden tailgating", "kredensial akses dibagikan", "titik masuk tidak dipantau"],
        "related_assets_en": ["access card readers", "biometric scanners", "electronic locks", "visitor management system", "badge printers", "turnstiles", "security guards", "access control software", "authentication servers", "entry logs"],
        "related_assets_id": ["pembaca kartu akses", "pemindai biometrik", "kunci elektronik", "sistem manajemen pengunjung", "pencetak lencana", "pintu putar", "penjaga keamanan", "perangkat lunak kontrol akses", "server autentikasi", "log masuk"],
        "security_principles_en": ["identification", "authentication", "authorization", "accountability", "physical access control", "non-repudiation"],
        "security_principles_id": ["identifikasi", "autentikasi", "otorisasi", "akuntabilitas", "kontrol akses fisik", "non-repudiasi"]
    },
    "A.7.3": {
        "keywords_en": ["secure office design", "office security", "workspace security", "internal security", "secure layout", "facility design", "security zoning", "protected workspace", "internal access control", "office isolation"],
        "keywords_id": ["desain kantor aman", "keamanan kantor", "keamanan ruang kerja", "keamanan internal", "tata letak aman", "desain fasilitas", "zona keamanan", "ruang kerja terlindungi", "kontrol akses internal", "isolasi kantor"],
        "audit_indicators_en": ["offices without secure design", "unsecured internal areas", "no security zoning", "public access to workspaces", "unprotected sensitive work areas", "no physical barriers between departments", "unsecured storage in offices", "lack of workspace security"],
        "audit_indicators_id": ["kantor tanpa desain aman", "area internal tidak aman", "tidak ada zona keamanan", "akses publik ke ruang kerja", "area kerja sensitif tidak terlindungi", "tidak ada penghalang fisik antar departemen", "penyimpanan tidak aman di kantor", "kurangnya keamanan ruang kerja"],
        "related_assets_en": ["office walls", "security partitions", "secure meeting rooms", "locked storage", "office doors", "security windows", "internal barriers", "secure furniture", "document safes", "security screens"],
        "related_assets_id": ["dinding kantor", "partisi keamanan", "ruang pertemuan aman", "penyimpanan terkunci", "pintu kantor", "jendela keamanan", "penghalang internal", "perabotan aman", "brankas dokumen", "layar keamanan"],
        "security_principles_en": ["segregation of duties", "need-to-know", "physical separation", "secure design", "internal controls", "zone security"],
        "security_principles_id": ["pemisahan tugas", "need-to-know", "pemisahan fisik", "desain aman", "kontrol internal", "keamanan zona"]
    },
    "A.7.4": {
        "keywords_en": ["delivery and loading areas", "loading dock security", "delivery access control", "goods receiving security", "external access points", "delivery vehicle screening", "cargo security", "loading bay control", "supply chain security", "delivery verification"],
        "keywords_id": ["area pengiriman dan pemuatan", "keamanan dermaga pemuatan", "kontrol akses pengiriman", "keamanan penerimaan barang", "titik akses eksternal", "pemeriksaan kendaraan pengiriman", "keamanan kargo", "kontrol dermaga pemuatan", "keamanan rantai pasok", "verifikasi pengiriman"],
        "audit_indicators_en": ["uncontrolled delivery access", "loading areas unmonitored", "delivery vehicles unscreened", "unauthorized deliveries accepted", "no delivery verification procedures", "loading dock accessible to public", "delivery person unescorted", "cargo unsecured"],
        "audit_indicators_id": ["akses pengiriman tidak terkontrol", "area pemuatan tidak dipantau", "kendaraan pengiriman tidak diperiksa", "pengiriman tidak sah diterima", "tidak ada prosedur verifikasi pengiriman", "dermaga pemuatan dapat diakses publik", "kurir pengiriman tanpa pendamping", "kargo tidak aman"],
        "related_assets_en": ["loading docks", "delivery gates", "cargo bays", "security cameras", "weighing scales", "delivery scanners", "vehicle barriers", "loading bay doors", "receiving areas", "delivery logs"],
        "related_assets_id": ["dermaga pemuatan", "gerbang pengiriman", "teluk kargo", "kamera keamanan", "timbangan", "pemindai pengiriman", "penghalang kendaraan", "pintu dermaga pemuatan", "area penerimaan", "log pengiriman"],
        "security_principles_en": ["access control", "supply chain security", "verification", "monitoring", "physical security", "inspection"],
        "security_principles_id": ["kontrol akses", "keamanan rantai pasok", "verifikasi", "pemantauan", "keamanan fisik", "pemeriksaan"]
    },
    "A.7.5": {
        "keywords_en": ["environmental threats", "natural disasters", "fire protection", "flood protection", "environmental controls", "disaster prevention", "environmental monitoring", "hazard protection", "emergency systems", "physical threat prevention"],
        "keywords_id": ["ancaman lingkungan", "bencana alam", "perlindungan kebakaran", "perlindungan banjir", "kontrol lingkungan", "pencegahan bencana", "pemantauan lingkungan", "perlindungan bahaya", "sistem darurat", "pencegahan ancaman fisik"],
        "audit_indicators_en": ["no fire protection system", "lack of environmental controls", "no disaster recovery plan", "fire suppression systems missing", "no flood protection measures", "environmental monitoring absent", "emergency exits blocked", "no emergency lighting"],
        "audit_indicators_id": ["tidak ada sistem perlindungan kebakaran", "kurangnya kontrol lingkungan", "tidak ada rencana pemulihan bencana", "sistem penekan kebakaran hilang", "tidak ada tindakan perlindungan banjir", "pemantauan lingkungan tidak ada", "pintu darurat terblokir", "tidak ada pencahayaan darurat"],
        "related_assets_en": ["fire suppression systems", "smoke detectors", "flood barriers", "HVAC systems", "environmental sensors", "emergency generators", "UPS systems", "fire extinguishers", "emergency lighting", "water sensors"],
        "related_assets_id": ["sistem penekan kebakaran", "detektor asap", "penghalang banjir", "sistem HVAC", "sensor lingkungan", "generator darurat", "sistem UPS", "alat pemadam api", "pencahayaan darurat", "sensor air"],
        "security_principles_en": ["availability", "disaster recovery", "preventive controls", "environmental security", "business continuity", "resilience"],
        "security_principles_id": ["ketersediaan", "pemulihan bencana", "kontrol pencegahan", "keamanan lingkungan", "kelangsungan bisnis", "resiliensi"]
    },
    "A.7.6": {
        "keywords_en": ["secure areas", "working in secure areas", "security clearances", "classified areas", "restricted access areas", "security zones", "clean desk policy", "secure workspace protocols", "area access authorization", "controlled workspace"],
        "keywords_id": ["area aman", "bekerja di area aman", "clearance keamanan", "area terklasifikasi", "area akses terbatas", "zona keamanan", "kebijakan meja bersih", "protokol ruang kerja aman", "otorisasi akses area", "ruang kerja terkontrol"],
        "audit_indicators_en": ["unauthorized access to secure areas", "no security clearance verification", "secure area protocols not followed", "unescorted visitors in secure areas", "security zone breaches", "unauthorized devices in secure areas", "clean desk policy violations", "lack of area supervision"],
        "audit_indicators_id": ["akses tidak sah ke area aman", "tidak ada verifikasi clearance keamanan", "protokol area aman tidak diikuti", "pengunjung tanpa pendamping di area aman", "pelanggaran zona keamanan", "perangkat tidak sah di area aman", "pelanggaran kebijakan meja bersih", "kurangnya pengawasan area"],
        "related_assets_en": ["secure area access cards", "security clearance badges", "area monitoring systems", "secure storage cabinets", "encrypted communication devices", "document safes", "security cameras", "visitor escorts", "access logs", "security checkpoints"],
        "related_assets_id": ["kartu akses area aman", "lencana clearance keamanan", "sistem pemantauan area", "kabinet penyimpanan aman", "perangkat komunikasi terenkripsi", "brankas dokumen", "kamera keamanan", "pendamping pengunjung", "log akses", "pos pemeriksaan keamanan"],
        "security_principles_en": ["need-to-know", "access control", "security clearance", "physical security", "zone protection", "classification"],
        "security_principles_id": ["need-to-know", "kontrol akses", "clearance keamanan", "keamanan fisik", "perlindungan zona", "klasifikasi"]
    },
    "A.7.7": {
        "keywords_en": ["clean desk policy", "clear screen policy", "information protection", "document security", "unattended workspace", "screen locking", "physical information security", "desk cleanliness", "unauthorized information access", "workspace security"],
        "keywords_id": ["kebijakan meja bersih", "kebijakan layar bersih", "perlindungan informasi", "keamanan dokumen", "ruang kerja tanpa pengawasan", "penguncian layar", "keamanan informasi fisik", "kebersihan meja", "akses informasi tidak sah", "keamanan ruang kerja"],
        "audit_indicators_en": ["sensitive documents left on desks", "unlocked computers", "no clean desk policy", "screens not locked when unattended", "confidential information visible", "documents not secured after hours", "open files in workspace", "no screen timeout"],
        "audit_indicators_id": ["dokumen sensitif ditinggalkan di meja", "komputer tidak terkunci", "tidak ada kebijakan meja bersih", "layar tidak terkunci saat ditinggal", "informasi rahasia terlihat", "dokumen tidak diamankan setelah jam kerja", "file terbuka di ruang kerja", "tidak ada timeout layar"],
        "related_assets_en": ["document shredders", "lockable cabinets", "screen locking software", "desk organizers", "security containers", "document safes", "privacy filters", "automatic logout systems", "clean desk signage", "secure disposal bins"],
        "related_assets_id": ["penghancur dokumen", "kabinet yang dapat dikunci", "perangkat lunak pengunci layar", "organizer meja", "kontainer keamanan", "brankas dokumen", "filter privasi", "sistem logout otomatis", "papan tanda meja bersih", "tempat sampah aman"],
        "security_principles_en": ["information confidentiality", "physical security", "access control", "clean desk practices", "unattended equipment security", "document protection"],
        "security_principles_id": ["kerahasiaan informasi", "keamanan fisik", "kontrol akses", "praktik meja bersih", "keamanan peralatan tanpa pengawasan", "perlindungan dokumen"]
    },
    "A.7.8": {
        "keywords_en": ["equipment placement", "equipment protection", "secure equipment location", "hardware security", "equipment positioning", "damage prevention", "equipment siting", "physical equipment security", "environmental protection", "equipment storage"],
        "keywords_id": ["penempatan peralatan", "perlindungan peralatan", "lokasi peralatan aman", "keamanan perangkat keras", "posisi peralatan", "pencegahan kerusakan", "penempatan peralatan", "keamanan peralatan fisik", "perlindungan lingkungan", "penyimpanan peralatan"],
        "audit_indicators_en": ["equipment in hazardous locations", "inadequate equipment protection", "equipment exposed to damage", "poor equipment placement", "no environmental protection", "equipment accessibility issues", "unsafe equipment positioning", "lack of equipment security"],
        "audit_indicators_id": ["peralatan di lokasi berbahaya", "perlindungan peralatan tidak memadai", "peralatan terpapar kerusakan", "penempatan peralatan buruk", "tidak ada perlindungan lingkungan", "masalah aksesibilitas peralatan", "posisi peralatan tidak aman", "kurangnya keamanan peralatan"],
        "related_assets_en": ["server racks", "equipment cabinets", "cable management", "security enclosures", "environmental sensors", "protective covers", "mounting hardware", "equipment shelves", "security cages", "protective barriers"],
        "related_assets_id": ["rak server", "kabinet peralatan", "manajemen kabel", "enklosur keamanan", "sensor lingkungan", "penutup pelindung", "perangkat keras pemasangan", "rak peralatan", "kurung keamanan", "penghalang pelindung"],
        "security_principles_en": ["physical security", "equipment protection", "environmental safety", "damage prevention", "secure placement", "hardware protection"],
        "security_principles_id": ["keamanan fisik", "perlindungan peralatan", "keselamatan lingkungan", "pencegahan kerusakan", "penempatan aman", "perlindungan perangkat keras"]
    },
    "A.7.9": {
        "keywords_en": ["off-site asset security", "remote equipment security", "asset tracking", "off-site equipment", "mobile asset security", "remote equipment protection", "asset inventory", "equipment accountability", "off-site access control", "mobile device security"],
        "keywords_id": ["keamanan aset off-site", "keamanan peralatan jarak jauh", "pelacakan aset", "peralatan off-site", "keamanan aset seluler", "perlindungan peralatan jarak jauh", "inventaris aset", "akuntabilitas peralatan", "kontrol akses off-site", "keamanan perangkat seluler"],
        "audit_indicators_en": ["untracked off-site equipment", "off-site assets unprotected", "no off-site security policies", "lost off-site equipment", "unauthorized off-site access", "equipment taken off-site without approval", "no asset accountability", "off-site security breaches"],
        "audit_indicators_id": ["peralatan off-site tidak dilacak", "aset off-site tidak terlindungi", "tidak ada kebijakan keamanan off-site", "peralatan off-site hilang", "akses off-site tidak sah", "peralatan dibawa off-site tanpa persetujuan", "tidak ada akuntabilitas aset", "pelanggaran keamanan off-site"],
        "related_assets_en": ["mobile devices", "laptops", "remote servers", "portable storage", "off-site backup systems", "tracking devices", "security cables", "encryption software", "asset tags", "remote monitoring systems"],
        "related_assets_id": ["perangkat seluler", "laptop", "server jarak jauh", "penyimpanan portabel", "sistem cadangan off-site", "perangkat pelacakan", "kabel keamanan", "perangkat lunak enkripsi", "tag aset", "sistem pemantauan jarak jauh"],
        "security_principles_en": ["asset protection", "physical security", "tracking and accountability", "remote security", "encryption", "access control"],
        "security_principles_id": ["perlindungan aset", "keamanan fisik", "pelacakan dan akuntabilitas", "keamanan jarak jauh", "enkripsi", "kontrol akses"]
    },
    "A.7.10": {
        "keywords_en": ["storage media", "media handling", "data storage security", "removable media", "media disposal", "media encryption", "media access control", "backup media", "storage media protection", "media lifecycle"],
        "keywords_id": ["media penyimpanan", "penanganan media", "keamanan penyimpanan data", "media yang dapat dilepas", "pembuangan media", "enkripsi media", "kontrol akses media", "media cadangan", "perlindungan media penyimpanan", "siklus hidup media"],
        "audit_indicators_en": ["unsecured storage media", "unencrypted sensitive media", "improper media disposal", "no media handling procedures", "media access not controlled", "lost storage media", "unauthorized media copying", "media inventory missing"],
        "audit_indicators_id": ["media penyimpanan tidak aman", "media sensitif tidak dienkripsi", "pembuangan media tidak tepat", "tidak ada prosedur penanganan media", "akses media tidak dikontrol", "media penyimpanan hilang", "penyalinan media tidak sah", "inventaris media hilang"],
        "related_assets_en": ["USB drives", "external hard drives", "backup tapes", "optical disks", "memory cards", "encrypted storage devices", "media vaults", "storage cabinets", "destruction equipment", "media inventory systems"],
        "related_assets_id": ["drive USB", "hard drive eksternal", "pita cadangan", "disk optik", "kartu memori", "perangkat penyimpanan terenkripsi", "brankas media", "kabinet penyimpanan", "peralatan penghancuran", "sistem inventaris media"],
        "security_principles_en": ["data confidentiality", "media security", "encryption", "access control", "secure disposal", "data lifecycle management"],
        "security_principles_id": ["kerahasiaan data", "keamanan media", "enkripsi", "kontrol akses", "pembuangan aman", "manajemen siklus hidup data"]
    },
    "A.7.11": {
        "keywords_en": ["supporting utilities", "power supply", "utility infrastructure", "redundant power", "UPS systems", "backup generators", "utility security", "power backup", "environmental utilities", "utility reliability"],
        "keywords_id": ["utilitas pendukung", "pasokan daya", "infrastruktur utilitas", "daya redundan", "sistem UPS", "generator cadangan", "keamanan utilitas", "cadangan daya", "utilitas lingkungan", "keandalan utilitas"],
        "audit_indicators_en": ["no backup power supply", "UPS systems not maintained", "generator testing neglected", "single point of failure in utilities", "utility capacity insufficient", "power supply unstable", "no utility monitoring", "backup power systems fail during outage"],
        "audit_indicators_id": ["tidak ada pasokan daya cadangan", "sistem UPS tidak dipelihara", "pengujian generator diabaikan", "titik tunggal kegagalan dalam utilitas", "kapasitas utilitas tidak mencukupi", "pasokan daya tidak stabil", "tidak ada pemantauan utilitas", "sistem daya cadangan gagal selama pemadaman"],
        "related_assets_en": ["UPS systems", "backup generators", "power distribution units", "environmental control systems", "utility monitoring systems", "transfer switches", "power cables", "backup batteries", "utility meters", "alarm systems"],
        "related_assets_id": ["sistem UPS", "generator cadangan", "unit distribusi daya", "sistem kontrol lingkungan", "sistem pemantauan utilitas", "sakelar transfer", "kabel daya", "baterai cadangan", "meter utilitas", "sistem alarm"],
        "security_principles_en": ["availability", "redundancy", "business continuity", "preventive maintenance", "resilience", "capacity planning"],
        "security_principles_id": ["ketersediaan", "redundansi", "kelangsungan bisnis", "pemeliharaan pencegahan", "resiliensi", "perencanaan kapasitas"]
    },
    "A.7.12": {
        "keywords_en": ["cabling security", "network cable protection", "physical cable security", "cable routing", "unauthorized cable connections", "cable management", "network infrastructure security", "cable access control", "cable labeling", "physical network security"],
        "keywords_id": ["keamanan pengkabelan", "perlindungan kabel jaringan", "keamanan kabel fisik", "rute kabel", "koneksi kabel tidak sah", "manajemen kabel", "keamanan infrastruktur jaringan", "kontrol akses kabel", "pelabelan kabel", "keamanan jaringan fisik"],
        "audit_indicators_en": ["unprotected network cables", "unlabeled cables", "unauthorized cable connections", "cables accessible to unauthorized persons", "no cable inventory", "poor cable management", "cable routing insecure", "network cables exposed"],
        "audit_indicators_id": ["kabel jaringan tidak terlindungi", "kabel tidak berlabel", "koneksi kabel tidak sah", "kabel dapat diakses oleh orang tidak sah", "tidak ada inventaris kabel", "manajemen kabel buruk", "rute kabel tidak aman", "kabel jaringan terpapar"],
        "related_assets_en": ["network cables", "fiber optic cables", "cable trays", "cable labels", "patch panels", "cable locks", "cable conduits", "network racks", "cable management systems", "security seals"],
        "related_assets_id": ["kabel jaringan", "kabel serat optik", "baki kabel", "label kabel", "panel tambalan", "kunci kabel", "konduit kabel", "rak jaringan", "sistem manajemen kabel", "segel keamanan"],
        "security_principles_en": ["physical security", "network security", "access control", "cable management", "infrastructure protection", "asset identification"],
        "security_principles_id": ["keamanan fisik", "keamanan jaringan", "kontrol akses", "manajemen kabel", "perlindungan infrastruktur", "identifikasi aset"]
    },
    "A.7.13": {
        "keywords_en": ["equipment maintenance", "maintenance procedures", "preventive maintenance", "equipment servicing", "maintenance security", "maintenance access control", "maintenance logs", "equipment reliability", "scheduled maintenance", "maintenance documentation"],
        "keywords_id": ["pemeliharaan peralatan", "prosedur pemeliharaan", "pemeliharaan pencegahan", "perawatan peralatan", "keamanan pemeliharaan", "kontrol akses pemeliharaan", "log pemeliharaan", "keandalan peralatan", "pemeliharaan terjadwal", "dokumentasi pemeliharaan"],
        "audit_indicators_en": ["no maintenance schedule", "maintenance not documented", "unauthorized maintenance personnel", "maintenance access not controlled", "no maintenance logs", "preventive maintenance neglected", "equipment failure due to poor maintenance", "maintenance records incomplete"],
        "audit_indicators_id": ["tidak ada jadwal pemeliharaan", "pemeliharaan tidak didokumentasikan", "personel pemeliharaan tidak sah", "akses pemeliharaan tidak dikontrol", "tidak ada log pemeliharaan", "pemeliharaan pencegahan diabaikan", "kegagalan peralatan karena pemeliharaan buruk", "catatan pemeliharaan tidak lengkap"],
        "related_assets_en": ["maintenance tools", "service equipment", "maintenance logs", "spare parts", "service contracts", "maintenance manuals", "diagnostic equipment", "calibration tools", "testing equipment", "maintenance schedules"],
        "related_assets_id": ["alat pemeliharaan", "peralatan layanan", "log pemeliharaan", "suku cadang", "kontrak layanan", "manual pemeliharaan", "peralatan diagnostik", "alat kalibrasi", "peralatan pengujian", "jadwal pemeliharaan"],
        "security_principles_en": ["preventive maintenance", "equipment reliability", "maintenance access control", "documentation", "service continuity", "asset lifecycle"],
        "security_principles_id": ["pemeliharaan pencegahan", "keandalan peralatan", "kontrol akses pemeliharaan", "dokumentasi", "kelangsungan layanan", "siklus hidup aset"]
    },
    "A.7.14": {
        "keywords_en": ["equipment disposal", "secure disposal", "equipment reuse", "data sanitization", "secure disposal procedures", "equipment destruction", "data wiping", "asset decommissioning", "disposal documentation", "environmental disposal"],
        "keywords_id": ["pembuangan peralatan", "pembuangan aman", "penggunaan kembali peralatan", "sanitasi data", "prosedur pembuangan aman", "penghancuran peralatan", "penghapusan data", "dekomisioning aset", "dokumentasi pembuangan", "pembuangan lingkungan"],
        "audit_indicators_en": ["equipment disposed without data wiping", "no secure disposal procedures", "sensitive data on disposed equipment", "no disposal documentation", "equipment sold without sanitization", "unauthorized equipment disposal", "disposal records incomplete", "environmental regulations violated"],
        "audit_indicators_id": ["peralatan dibuang tanpa penghapusan data", "tidak ada prosedur pembuangan aman", "data sensitif pada peralatan yang dibuang", "tidak ada dokumentasi pembuangan", "peralatan dijual tanpa sanitasi", "pembuangan peralatan tidak sah", "catatan pembuangan tidak lengkap", "regulasi lingkungan dilanggar"],
        "related_assets_en": ["data wiping software", "degaussing equipment", "shredding machines", "disposal containers", "documentation systems", "destruction certificates", "sanitization tools", "inventory tracking", "recycling services", "disposal vendors"],
        "related_assets_id": ["perangkat lunak penghapusan data", "peralatan degaussing", "mesin penghancuran", "kontainer pembuangan", "sistem dokumentasi", "sertifikat penghancuran", "alat sanitasi", "pelacakan inventaris", "layanan daur ulang", "vendor pembuangan"],
        "security_principles_en": ["data sanitization", "secure disposal", "environmental compliance", "documentation", "asset lifecycle", "data protection"],
        "security_principles_id": ["sanitasi data", "pembuangan aman", "kepatuhan lingkungan", "dokumentasi", "siklus hidup aset", "perlindungan data"]
    }
}

# Apply enrichments to controls
enriched_count = 0
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
        enriched_count += 1

# Save the updated controls
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(controls, f, indent=2, ensure_ascii=False)

print(f"Enriched {enriched_count} A.7 controls")
print("File saved successfully")
