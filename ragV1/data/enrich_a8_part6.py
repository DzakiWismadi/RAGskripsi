import json

with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'r', encoding='utf-8') as f:
    controls = json.load(f)

enrichments = {
    "A.8.27": {
        "keywords_en": ["secure system architecture", "secure engineering principles", "security by design", "threat modeling", "secure design patterns", "defense in depth", "least privilege", "secure development lifecycle"],
        "keywords_id": ["arsitektur sistem aman", "prinsip rekayasa aman", "keamanan sejak awal", "pemodelan ancaman", "pola desain aman", "pertahanan berlapis", "hak istimewa最小", "siklus pengembangan aman"],
        "audit_indicators_en": ["no secure architecture review", "lack of threat modeling", "security not considered in design", "no defense in depth strategy", "insecure design patterns", "no security architecture documentation", "missing secure design principles"],
        "audit_indicators_id": ["tidak ada tinjauan arsitektur aman", "tidak ada pemodelan ancaman", "keamanan tidak dipertimbangkan dalam desain", "tidak ada strategi pertahanan berlapis", "pola desain tidak aman", "tidak ada dokumentasi arsitektur keamanan", "kurang prinsip desain aman"],
        "related_assets_en": ["system architecture diagrams", "design documents", "threat models", "security requirements", "architecture review boards", "secure design guidelines"],
        "related_assets_id": ["diagram arsitektur sistem", "dokumen desain", "model ancaman", "persyaratan keamanan", "board tinjauan arsitektur", "panduan desain aman"],
        "security_principles_en": ["security by design", "defense in depth", "least privilege", "fail-safe defaults", "secure architecture", "threat modeling"],
        "security_principles_id": ["keamanan sejak awal", "pertahanan berlapis", "hak istimewa最小", "default aman", "arsitektur aman", "pemodelan ancaman"]
    }
}

count = 0
for control in controls:
    if control['control_id'] in enrichments:
        control.update(enrichments[control['control_id']])
        count += 1

with open(r'D:\Hilmi\Coding\MasterFolderSkripsi\RAG\ragV1\data\iso_controls_enriched.json', 'w', encoding='utf-8') as f:
    json.dump(controls, f, ensure_ascii=False, indent=2)

print(f"Enriched {count} controls")
print("File saved successfully")
