import json

# Read the current enriched controls
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    controls = json.load(f)

# Define enrichments for A.8.19 through A.8.22
enrichments = {
    "A.8.19": {
        "keywords_en": ["software installation", "operational systems", "software updates", "patch management", "software configuration", "installation procedures", "software approval", "version control", "software compatibility", "installation testing"],
        "keywords_id": ["instalasi perangkat lunak", "sistem operasional", "pembaruan perangkat lunak", "manajemen patch", "konfigurasi perangkat lunak", "prosedur instalasi", "persetujuan perangkat lunak", "kontrol versi", "kompatibilitas perangkat lunak", "pengujian instalasi"],
        "audit_indicators_en": ["unauthorized software installed", "no software installation procedures", "software installed without approval", "outdated software versions", "no patch management process", "incompatible software versions", "software installation logs not maintained", "software not tested before deployment"],
        "audit_indicators_id": ["perangkat lunak tidak resmi terinstal", "tidak ada prosedur instalasi perangkat lunak", "perangkat lunak diinstal tanpa persetujuan", "versi perangkat lunak usang", "tidak ada proses manajemen patch", "versi perangkat lunak tidak kompatibel", "log instalasi perangkat lunak tidak dipelihara", "perangkat lunak tidak diuji sebelum deployment"],
        "related_assets_en": ["production servers", "workstations", "application servers", "database servers", "development systems", "testing environments", "software repositories", "deployment tools"],
        "related_assets_id": ["server produksi", "stasiun kerja", "server aplikasi", "server database", "sistem pengembangan", "lingkungan pengujian", "repositori perangkat lunak", "alat deployment"],
        "security_principles_en": ["change management", "software integrity", "configuration management", "version control", "approval processes", "testing procedures", "patch management"],
        "security_principles_id": ["manajemen perubahan", "integritas perangkat lunak", "manajemen konfigurasi", "kontrol versi", "proses persetujuan", "prosedur pengujian", "manajemen patch"]
    },
    "A.8.20": {
        "keywords_en": ["network security", "network controls", "network segmentation", "firewall configuration", "network monitoring", "intrusion detection", "network access control", "network architecture", "network services", "network protocols"],
        "keywords_id": ["keamanan jaringan", "kontrol jaringan", "segmentasi jaringan", "konfigurasi firewall", "pemantauan jaringan", "deteksi intrusi", "kontrol akses jaringan", "arsitektur jaringan", "layanan jaringan", "protokol jaringan"],
        "audit_indicators_en": ["unauthorized network access", "firewall rules not configured", "no network monitoring", "unsegmented network", "missing network controls", "outdated network security", "unauthorized network services", "network vulnerabilities"],
        "audit_indicators_id": ["akses jaringan tidak resmi", "aturan firewall tidak dikonfigurasi", "tidak ada pemantauan jaringan", "jaringan tidak tersegmentasi", "kontrol jaringan hilang", "keamanan jaringan usang", "layanan jaringan tidak resmi", "kerentanan jaringan"],
        "related_assets_en": ["network firewalls", "routers", "switches", "intrusion detection systems", "network monitors", "VPN gateways", "load balancers", "network segmentation devices"],
        "related_assets_id": ["firewall jaringan", "router", "switch", "sistem deteksi intrusi", "monitor jaringan", "gateway VPN", "penyeimbang beban", "perangkat segmentasi jaringan"],
        "security_principles_en": ["defense in depth", "network segmentation", "least privilege", "monitoring and detection", "access control", "secure configuration", "network architecture"],
        "security_principles_id": ["pertahanan berlapis", "segmentasi jaringan", "hak istimewa最小", "pemantauan dan deteksi", "kontrol akses", "konfigurasi aman", "arsitektur jaringan"]
    },
    "A.8.21": {
        "keywords_en": ["network services security", "service agreements", "service level agreements", "network service providers", "service monitoring", "service continuity", "service availability", "service contracts", "service performance", "service security"],
        "keywords_id": ["keamanan layanan jaringan", "perjanjian layanan", "perjanjian tingkat layanan", "penyedia layanan jaringan", "pemantauan layanan", "kelangsungan layanan", "ketersediaan layanan", "kontrak layanan", "kinerja layanan", "keamanan layanan"],
        "audit_indicators_en": ["no service agreements in place", "service levels not monitored", "service interruptions not reported", "service security not defined", "service contracts not reviewed", "service availability not guaranteed", "service performance not measured", "service dependencies not identified"],
        "audit_indicators_id": ["tidak ada perjanjian layanan", "tingkat layanan tidak dipantau", "gangguan layanan tidak dilaporkan", "keamanan layanan tidak didefinisikan", "kontrak layanan tidak ditinjau", "ketersediaan layanan tidak dijamin", "kinerja layanan tidak diukur", "dependensi layanan tidak diidentifikasi"],
        "related_assets_en": ["network service contracts", "service level agreements", "service monitoring tools", "network service providers", "service infrastructure", "service delivery platforms", "service management systems"],
        "related_assets_id": ["kontrak layanan jaringan", "perjanjian tingkat layanan", "alat pemantauan layanan", "penyedia layanan jaringan", "infrastruktur layanan", "platform pengiriman layanan", "sistem manajemen layanan"],
        "security_principles_en": ["service availability", "service continuity", "contract management", "performance monitoring", "service level management", "risk management", "vendor management"],
        "security_principles_id": ["ketersediaan layanan", "kelangsungan layanan", "manajemen kontrak", "pemantauan kinerja", "manajemen tingkat layanan", "manajemen risiko", "manajemen vendor"]
    },
    "A.8.22": {
        "keywords_en": ["network segregation", "network separation", "security zones", "dmz", "network isolation", "segmented networks", "network filtering", "traffic separation", "network boundaries", "isolated network segments"],
        "keywords_id": ["segregasi jaringan", "pemisahan jaringan", "zona keamanan", "dmz", "isolasi jaringan", "jaringan tersegmentasi", "filtrasi jaringan", "pemisahan trafik", "batas jaringan", "segmen jaringan terisolasi"],
        "audit_indicators_en": ["no network segregation implemented", "security zones not defined", "traffic not segregated", "no network isolation", "unsegmented network architecture", "missing network boundaries", "all systems on same network", "no DMZ configured"],
        "audit_indicators_id": ["segregasi jaringan tidak diimplementasikan", "zona keamanan tidak didefinisikan", "trafik tidak tersegregasi", "tidak ada isolasi jaringan", "arsitektur jaringan tidak tersegmentasi", "batas jaringan hilang", "semua sistem di jaringan sama", "tidak ada DMZ dikonfigurasi"],
        "related_assets_en": ["network segmentation devices", "firewalls", "vlans", "dmz networks", "security gateways", "network separators", "isolation appliances", "zone-based firewalls"],
        "related_assets_id": ["perangkat segmentasi jaringan", "firewall", "vlan", "jaringan dmz", "gateway keamanan", "pemisah jaringan", "aplikasi isolasi", "firewall berbasis zona"],
        "security_principles_en": ["network segregation", "defense in depth", "least privilege", "compartmentalization", "zone-based security", "traffic separation", "network isolation"],
        "security_principles_id": ["segregasi jaringan", "pertahanan berlapis", "hak istimewa最小", "kompartimentalisasi", "keamanan berbasis zona", "pemisahan trafik", "isolasi jaringan"]
    }
}

# Update controls with enrichment
updated_count = 0
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
        updated_count += 1

# Save the updated controls
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(controls, f, ensure_ascii=False, indent=2)

print(f"Enriched {updated_count} A.8 controls (part 3)")
print("File saved successfully")
