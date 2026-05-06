import json

# Read the enriched controls
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    controls = json.load(f)

# Enrichment dictionary for A.8.23 and A.8.24
enrichments = {
    "A.8.23": {
        "keywords_en": ["web filtering", "internet access control", "URL blocking", "content filtering", "web proxy", "browser security", "malicious websites", "phishing prevention", "web categorization", "internet policy enforcement"],
        "keywords_id": ["penyaringan web", "kontrol akses internet", "pemblokiran URL", "penyaringan konten", "proxy web", "keamanan browser", "situs web berbahaya", "pencegahan phishing", "kategorisasi web", "penegakan kebijakan internet"],
        "audit_indicators_en": ["no web filtering implemented", "unrestricted internet access", "employees accessing malicious websites", "no web proxy configuration", "web filtering logs not maintained", "bypassing web filters", "inappropriate web content accessible", "no web usage monitoring"],
        "audit_indicators_id": ["tidak ada penyaringan web", "akses internet tanpa batasan", "karyawan mengakses situs berbahaya", "tidak ada konfigurasi proxy web", "log penyaringan web tidak dipelihara", "menghindari penyaringan web", "konten web tidak pantas dapat diakses", "tidak ada pemantauan penggunaan web"],
        "related_assets_en": ["web proxy servers", "firewalls", "secure web gateways", "content filtering appliances", "internet routers", "DNS servers", "web browsers", "network perimeter devices"],
        "related_assets_id": ["server proxy web", "firewall", "gerbang web aman", "appliance penyaringan konten", "router internet", "server DNS", "browser web", "perangkat perimeter jaringan"],
        "security_principles_en": ["defense in depth", "internet security", "content control", "threat prevention", "policy enforcement", "network segmentation"],
        "security_principles_id": ["pertahanan berlapis", "keamanan internet", "kontrol konten", "pencegahan ancaman", "penegakan kebijakan", "segmentasi jaringan"]
    },
    "A.8.24": {
        "keywords_en": ["cryptography", "encryption", "decryption", "cryptographic keys", "key management", "AES encryption", "RSA encryption", "data encryption at rest", "data encryption in transit", "cryptographic algorithms"],
        "keywords_id": ["kriptografi", "enkripsi", "dekripsi", "kunci kriptografis", "manajemen kunci", "enkripsi AES", "enkripsi RSA", "enkripsi data diam", "enkripsi data dalam transmisi", "algoritma kriptografis"],
        "audit_indicators_en": ["weak encryption algorithms", "no encryption for sensitive data", "improper key management", "expired encryption keys", "unencrypted data transmission", "missing encryption controls", "inadequate key length", "no key rotation policy"],
        "audit_indicators_id": ["algoritma enkripsi lemah", "tidak ada enkripsi untuk data sensitif", "manajemen kunci tidak tepat", "kunci enkripsi kedaluwarsa", "transmisi data tidak terenkripsi", "kontrol enkripsi hilang", "panjang kunci tidak adekuat", "tidak ada kebijakan rotasi kunci"],
        "related_assets_en": ["hardware security modules", "encryption appliances", "key management systems", "encrypted storage devices", "SSL/TLS certificates", "cryptographic software", "secure key storage", "encrypted databases"],
        "related_assets_id": ["modul keamanan perangkat keras", "appliance enkripsi", "sistem manajemen kunci", "perangkat penyimpanan terenkripsi", "sertifikat SSL/TLS", "perangkat lunak kriptografis", "penyimpanan kunci aman", "database terenkripsi"],
        "security_principles_en": ["confidentiality", "data protection", "key security", "algorithm strength", "cryptographic agility", "secure key lifecycle"],
        "security_principles_id": ["kerahasiaan", "perlindungan data", "keamanan kunci", "kekuatan algoritma", "agilitas kriptografis", "siklus hidup kunci aman"]
    }
}

# Apply enrichment
count = 0
for control in controls:
    if control['control_id'] in enrichments:
        enrich = enrichments[control['control_id']]
        control['keywords_en'] = enrich['keywords_en']
        control['keywords_id'] = enrich['keywords_id']
        control['audit_indicators_en'] = enrich['audit_indicators_en']
        control['audit_indicators_id'] = enrich['audit_indicators_id']
        control['related_assets_en'] = enrich['related_assets_en']
        control['related_assets_id'] = enrich['related_assets_id']
        control['security_principles_en'] = enrich['security_principles_en']
        control['security_principles_id'] = enrich['security_principles_id']
        count += 1

# Save back to file
with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(controls, f, ensure_ascii=False, indent=2)

print(f"Enriched {count} A.8 controls (part 4)")
print("File saved successfully")
