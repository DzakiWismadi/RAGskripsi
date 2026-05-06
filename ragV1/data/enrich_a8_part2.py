import json

# Read current enriched controls
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    controls = json.load(f)

# Define enrichment for A.8.13 - A.8.18
enrichments_a8_part2 = {
    "A.8.13": {
        "keywords_en": ["information backup", "backup testing", "backup restoration", "backup retention", "backup storage", "backup encryption", "backup frequency", "backup verification", "backup media", "backup recovery"],
        "keywords_id": ["backup informasi", "pengujian backup", "pemulihan backup", "retensi backup", "penyimpanan backup", "enkripsi backup", "frekuensi backup", "verifikasi backup", "media backup", "pemulihan backup"],
        "audit_indicators_en": ["no backup procedures documented", "backups not tested regularly", "no backup restoration tests", "backups stored at same location as originals", "backup retention period not defined", "backup encryption not implemented", "backup logs not maintained", "backup media not properly labeled"],
        "audit_indicators_id": ["tidak ada prosedur backup", "backup tidak diuji secara berkala", "tidak ada uji pemulihan backup", "backup disimpan di lokasi yang sama dengan aslinya", "periode retensi backup tidak didefinisikan", "enkripsi backup tidak diimplementasikan", "log backup tidak dipelihara", "media backup tidak berlabel dengan benar"],
        "related_assets_en": ["backup servers", "tape drives", "cloud backup storage", "external hard drives", "backup software", "backup vaults", "backup media", "backup appliances", "off-site storage", "backup repositories"],
        "related_assets_id": ["server backup", "drive tape", "penyimpanan backup cloud", "hard drive eksternal", "perangkat lunak backup", "vault backup", "media backup", "appliance backup", "penyimpanan off-site", "repositori backup"],
        "security_principles_en": ["availability", "confidentiality", "integrity", "reliability", "recoverability", "data persistence"],
        "security_principles_id": ["ketersediaan", "kerahasiaan", "integritas", "keandalan", "kemampuan pemulihan", "persistensi data"]
    },
    "A.8.14": {
        "keywords_en": ["redundancy", "high availability", "failover systems", "load balancing", "clustering", "disaster recovery", "backup facilities", "redundant power", "redundant cooling", "fault tolerance"],
        "keywords_id": ["redundansi", "ketersediaan tinggi", "sistem failover", "load balancing", "klastering", "pemulihan bencana", "fasilitas backup", "daya redundan", "pendinginan redundan", "toleransi kesalahan"],
        "audit_indicators_en": ["no redundant systems implemented", "single point of failure exists", "failover not tested", "no backup power supply", "load balancing not configured", "clustering not implemented", "redundant systems not maintained", "disaster recovery site not established"],
        "audit_indicators_id": ["tidak ada sistem redundan", "titik kegagalan tunggal ada", "failover tidak diuji", "tidak ada pasokan daya backup", "load balancing tidak dikonfigurasi", "klastering tidak diimplementasikan", "sistem redundan tidak dipelihara", "situs pemulihan bencana tidak didirikan"],
        "related_assets_en": ["redundant servers", "load balancers", "UPS systems", "backup generators", "clustered systems", "failover servers", "secondary data centers", "redundant network switches", "storage arrays", "cooling systems"],
        "related_assets_id": ["server redundan", "load balancer", "sistem UPS", "generator backup", "sistem klaster", "server failover", "pusat data sekunder", "switch jaringan redundan", "array penyimpanan", "sistem pendingin"],
        "security_principles_en": ["availability", "reliability", "fault tolerance", "resilience", "business continuity", "operational continuity"],
        "security_principles_id": ["ketersediaan", "keandalan", "toleransi kesalahan", "resiliensi", "kelangsungan bisnis", "kelangsungan operasional"]
    },
    "A.8.15": {
        "keywords_en": ["logging", "event logging", "audit trails", "log collection", "log analysis", "log retention", "log protection", "security logs", "system logs", "audit records"],
        "keywords_id": ["pencatatan log", "logging peristiwa", "jejak audit", "pengumpulan log", "analisis log", "retensi log", "perlindungan log", "log keamanan", "log sistem", "catatan audit"],
        "audit_indicators_en": ["logging not enabled", "logs not reviewed regularly", "log retention period too short", "logs not protected from tampering", "no centralized log collection", "audit trails incomplete", "log files deleted prematurely", "no log analysis procedures"],
        "audit_indicators_id": ["logging tidak diaktifkan", "log tidak ditinjau secara berkala", "periode retensi log terlalu singkat", "log tidak dilindungi dari penggerebekan", "tidak ada pengumpulan log terpusat", "jejak audit tidak lengkap", "file log dihapus sebelum waktunya", "tidak ada prosedur analisis log"],
        "related_assets_en": ["SIEM systems", "log servers", "syslog servers", "audit servers", "log storage", "log analyzers", "event collectors", "log management tools", "audit databases", "log aggregation systems"],
        "related_assets_id": ["sistem SIEM", "server log", "server syslog", "server audit", "penyimpanan log", "penganalisis log", "kolektor peristiwa", "alat manajemen log", "database audit", "sistem agregasi log"],
        "security_principles_en": ["accountability", "non-repudiation", "auditability", "traceability", "forensic readiness", "incident detection"],
        "security_principles_id": ["akuntabilitas", "non-repudiasi", "kelayakan audit", "kemampuan pelacakan", "kesiapan forensik", "deteksi insiden"]
    },
    "A.8.16": {
        "keywords_en": ["monitoring", "intrusion detection", "security monitoring", "network monitoring", "system monitoring", "anomaly detection", "security alerts", "monitoring dashboards", "real-time monitoring", "threat detection"],
        "keywords_id": ["pemantauan", "deteksi intrusi", "pemantauan keamanan", "pemantauan jaringan", "pemantauan sistem", "deteksi anomali", "peringatan keamanan", "dasbor pemantauan", "pemantauan real-time", "deteksi ancaman"],
        "audit_indicators_en": ["no monitoring system in place", "security events not monitored", "alerts not responded to", "no intrusion detection system", "monitoring coverage incomplete", "false positive rate too high", "monitoring logs not reviewed", "no escalation procedures for alerts"],
        "audit_indicators_id": ["tidak ada sistem pemantauan", "peristiwa keamanan tidak dipantau", "peringatan tidak ditanggapi", "tidak ada sistem deteksi intrusi", "cakupan pemantauan tidak lengkap", "tingkat false positive terlalu tinggi", "log pemantauan tidak ditinjau", "tidak ada prosedur eskalasi untuk peringatan"],
        "related_assets_en": ["IDS systems", "IPS systems", "monitoring servers", "network probes", "security sensors", "monitoring consoles", "alert management systems", "SIEM platforms", "network taps", "traffic analyzers"],
        "related_assets_id": ["sistem IDS", "sistem IPS", "server pemantauan", "probe jaringan", "sensor keamanan", "konsol pemantauan", "sistem manajemen peringatan", "platform SIEM", "tap jaringan", "penganalisis trafik"],
        "security_principles_en": ["detection", "response", "visibility", "situational awareness", "threat intelligence", "incident response"],
        "security_principles_id": ["deteksi", "respons", "visibilitas", "kesadaran situasional", "kecerdasan ancaman", "respons insiden"]
    },
    "A.8.17": {
        "keywords_en": ["time synchronization", "NTP", "clock synchronization", "time accuracy", "time servers", "atomic clocks", "network time protocol", "system time", "timestamp accuracy", "time sources"],
        "keywords_id": ["sinkronisasi waktu", "NTP", "sinkronisasi jam", "akurasi waktu", "server waktu", "jam atom", "protokol waktu jaringan", "waktu sistem", "akurasi timestamp", "sumber waktu"],
        "audit_indicators_en": ["systems have incorrect time", "no NTP servers configured", "clocks not synchronized", "significant time drift between systems", "no redundant time sources", "time synchronization not monitored", "manual time adjustments made", "timestamp inconsistencies in logs"],
        "audit_indicators_id": ["sistem memiliki waktu yang salah", "tidak ada server NTP yang dikonfigurasi", "jam tidak disinkronkan", "drift waktu signifikan antar sistem", "tidak ada sumber waktu redundan", "sinkronisasi waktu tidak dipantau", "penyesuaian waktu manual dilakukan", "ketidakkonsistenan timestamp dalam log"],
        "related_assets_en": ["NTP servers", "time servers", "atomic clocks", "GPS time receivers", "NTP clients", "network switches", "routers", "servers", "workstations", "domain controllers"],
        "related_assets_id": ["server NTP", "server waktu", "jam atom", "penerima waktu GPS", "klien NTP", "switch jaringan", "router", "server", "workstation", "kontroler domain"],
        "security_principles_en": ["integrity", "accuracy", "consistency", "non-repudiation", "auditability", "traceability"],
        "security_principles_id": ["integritas", "akurasi", "konsistensi", "non-repudiasi", "kelayakan audit", "kemampuan pelacakan"]
    },
    "A.8.18": {
        "keywords_en": ["utility programs", "system utilities", "privileged tools", "administrative utilities", "system administration tools", "diagnostic tools", "system maintenance utilities", "utility access control", "utility logging", "utility usage monitoring"],
        "keywords_id": ["program utilitas", "utilitas sistem", "alat istimewa", "utilitas administratif", "alat administrasi sistem", "alat diagnostik", "utilitas pemeliharaan sistem", "kontrol akses utilitas", "logging utilitas", "pemantauan penggunaan utilitas"],
        "audit_indicators_en": ["utility programs not restricted", "excessive utility access granted", "utility usage not logged", "no approval process for utility access", "utility programs outdated", "unauthorized utility installations", "utility access not reviewed", "utility inventory incomplete"],
        "audit_indicators_id": ["program utilitas tidak dibatasi", "akses utilitas berlebihan diberikan", "penggunaan utilitas tidak dicatat", "tidak ada proses persetujuan untuk akses utilitas", "program utilitas usang", "instalasi utilitas tidak sah", "akses utilitas tidak ditinjau", "inventarisasi utilitas tidak lengkap"],
        "related_assets_en": ["system utilities", "diagnostic tools", "administrative consoles", "maintenance software", "system administration tools", "recovery utilities", "performance monitoring tools", "debugging tools", "system configuration tools", "utility libraries"],
        "related_assets_id": ["utilitas sistem", "alat diagnostik", "konsol administratif", "perangkat lunak pemeliharaan", "alat administrasi sistem", "utilitas pemulihan", "alat pemantauan kinerja", "alat debugging", "alat konfigurasi sistem", "pustaka utilitas"],
        "security_principles_en": ["access control", "accountability", "separation of duties", "least privilege", "auditability", "change management"],
        "security_principles_id": ["kontrol akses", "akuntabilitas", "pemisahan tugas", "hak istimewa minimum", "kelayakan audit", "manajemen perubahan"]
    }
}

# Apply enrichments
count = 0
for control in controls:
    if control['control_id'] in enrichments_a8_part2:
        for key, value in enrichments_a8_part2[control['control_id']].items():
            control[key] = value
        count += 1

# Save updated controls
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(controls, f, indent=2, ensure_ascii=False)

print(f"Enriched {count} A.8 controls (part 2)")
print("File saved successfully")
