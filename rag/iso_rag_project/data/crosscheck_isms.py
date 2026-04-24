"""
Crosscheck iso_controls.json and audit_gold_standard.csv against ISMS.md reference.
"""
import json
import csv
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(DATA_DIR)
REPO_ROOT = os.path.dirname(PROJECT_ROOT)

CONTROLS_PATH = os.path.join(DATA_DIR, "iso_controls.json")
CSV_PATH = os.path.join(DATA_DIR, "audit_gold_standard.csv")
ISMS_PATH = os.path.join(REPO_ROOT, "ISMS.md")

# Official ISMS reference: control_id -> official English name
# Parsed from the formatted ISMS.md table
ISMS_CONTROLS = {
    "A.5.1": "Policies for Information Security",
    "A.5.2": "Information Security Roles and Responsibilities",
    "A.5.3": "Segregation of Duties",
    "A.5.4": "Management Responsibilities",
    "A.5.5": "Contact With Authorities",
    "A.5.6": "Contact With Special Interest Groups",
    "A.5.7": "Threat Intelligence",
    "A.5.8": "Information Security in Project Management",
    "A.5.9": "Inventory of Information and Other Associated Assets",
    "A.5.10": "Acceptable Use of Information and Other Associated Assets",
    "A.5.11": "Return of Assets",
    "A.5.12": "Classification of Information",
    "A.5.13": "Labelling of Information",
    "A.5.14": "Information Transfer",
    "A.5.15": "Access Control",
    "A.5.16": "Identity Management",
    "A.5.17": "Authentication Information",
    "A.5.18": "Access Rights",
    "A.5.19": "Information Security in Supplier Relationships",
    "A.5.20": "Addressing Information Security Within Supplier Agreements",
    "A.5.21": "Managing Information Security in the ICT Supply Chain",
    "A.5.22": "Monitoring, Review and Change Management of Supplier Services",
    "A.5.23": "Information Security for Use of Cloud Services",
    "A.5.24": "Information Security Incident Management Planning and Preparation",
    "A.5.25": "Assessment and Decision on Information Security Events",
    "A.5.26": "Response to Information Security Incidents",
    "A.5.27": "Learning From Information Security Incidents",
    "A.5.28": "Collection of Evidence",
    "A.5.29": "Information Security During Disruption",
    "A.5.30": "ICT Readiness for Business Continuity",
    "A.5.31": "Legal, Statutory, Regulatory and Contractual Requirements",
    "A.5.32": "Intellectual Property Rights",
    "A.5.33": "Protection of Records",
    "A.5.34": "Privacy and Protection of PII",
    "A.5.35": "Independent Review of Information Security",
    "A.5.36": "Compliance With Policies, Rules and Standards for Information Security",
    "A.5.37": "Documented Operating Procedures",
    "A.6.1": "Screening",
    "A.6.2": "Terms and Conditions of Employment",
    "A.6.3": "Information Security Awareness, Education and Training",
    "A.6.4": "Disciplinary Process",
    "A.6.5": "Responsibilities After Termination or Change of Employment",
    "A.6.6": "Confidentiality or Non-Disclosure Agreements",
    "A.6.7": "Remote Working",
    "A.6.8": "Information Security Event Reporting",
    "A.7.1": "Physical Security Perimeters",
    "A.7.2": "Physical Entry",
    "A.7.3": "Securing Offices, Rooms and Facilities",
    "A.7.4": "Physical Security Monitoring",
    "A.7.5": "Protecting Against Physical and Environmental Threats",
    "A.7.6": "Working In Secure Areas",
    "A.7.7": "Clear Desk and Clear Screen",
    "A.7.8": "Equipment Siting and Protection",
    "A.7.9": "Security of Assets Off-Premises",
    "A.7.10": "Storage Media",
    "A.7.11": "Supporting Utilities",
    "A.7.12": "Cabling Security",
    "A.7.13": "Equipment Maintenance",
    "A.7.14": "Secure Disposal or Re-Use of Equipment",
    "A.8.1": "User Endpoint Devices",
    "A.8.2": "Privileged Access Rights",
    "A.8.3": "Information Access Restriction",
    "A.8.4": "Access to Source Code",
    "A.8.5": "Secure Authentication",
    "A.8.6": "Capacity Management",
    "A.8.7": "Protection Against Malware",
    "A.8.8": "Management of Technical Vulnerabilities",
    "A.8.9": "Configuration Management",
    "A.8.10": "Information Deletion",
    "A.8.11": "Data Masking",
    "A.8.12": "Data Leakage Prevention",
    "A.8.13": "Information Backup",
    "A.8.14": "Redundancy of Information Processing Facilities",
    "A.8.15": "Logging",
    "A.8.16": "Monitoring Activities",
    "A.8.17": "Clock Synchronization",
    "A.8.18": "Use of Privileged Utility Programs",
    "A.8.19": "Installation of Software on Operational Systems",
    "A.8.20": "Networks Security",
    "A.8.21": "Security of Network Services",
    "A.8.22": "Segregation of Networks",
    "A.8.23": "Web Filtering",
    "A.8.24": "Use of Cryptography",
    "A.8.25": "Secure Development Life Cycle",
    "A.8.26": "Application Security Requirements",
    "A.8.27": "Secure System Architecture and Engineering Principles",
    "A.8.28": "Secure Coding",
    "A.8.29": "Security Testing in Development and Acceptance",
    "A.8.30": "Outsourced Development",
    "A.8.31": "Separation of Development, Test and Production Environments",
    "A.8.32": "Change Management",
    "A.8.33": "Test Information",
    "A.8.34": "Protection of Information Systems During Audit Testing",
}

# Expected Indonesian title mapping (what our JSON should have)
# This maps official English -> expected Indonesian keyword for comparison
ENGLISH_TO_INDO_KEYWORDS = {
    "Policies for Information Security": "kebijakan keamanan informasi",
    "Information Security Roles and Responsibilities": "peran dan tanggung jawab",
    "Segregation of Duties": "pemisahan tugas",
    "Management Responsibilities": "pemisahan tugas",  # A.5.4 is actually "Management Responsibilities" not "Segregation"
    "Contact With Authorities": "kontak dengan otoritas",
    "Contact With Special Interest Groups": "kontak dengan kelompok",
    "Threat Intelligence": "intelijen ancaman",
    "Screening": "penyaringan",
    "Terms and Conditions of Employment": "syarat dan ketentuan",
    "Remote Working": "bekerja jarak jauh",
}


def main():
    # Load our controls
    with open(CONTROLS_PATH, "r", encoding="utf-8") as f:
        controls = json.load(f)

    json_map = {c["control_id"]: c["title"] for c in controls}

    # Load CSV
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        csv_rows = list(reader)
    csv_control_ids = set(r["control_id"].strip() for r in csv_rows)

    print("=" * 90)
    print("CROSSCHECK REPORT: iso_controls.json vs ISMS.md (Official ISO 27001:2022)")
    print("=" * 90)

    # 1. Check control IDs match
    isms_ids = set(ISMS_CONTROLS.keys())
    json_ids = set(json_map.keys())

    missing_in_json = isms_ids - json_ids
    extra_in_json = json_ids - isms_ids

    print(f"\n--- Control ID Check ---")
    print(f"ISMS.md controls: {len(isms_ids)}")
    print(f"iso_controls.json controls: {len(json_ids)}")

    if missing_in_json:
        print(f"\nMISSING in JSON (exists in ISMS.md but not in JSON):")
        for cid in sorted(missing_in_json):
            print(f"  {cid}: {ISMS_CONTROLS[cid]}")
    else:
        print(f"\nAll ISMS.md control IDs present in JSON: PASS")

    if extra_in_json:
        print(f"\nEXTRA in JSON (exists in JSON but not in ISMS.md):")
        for cid in sorted(extra_in_json):
            print(f"  {cid}: {json_map[cid]}")
    else:
        print(f"No extra control IDs in JSON: PASS")

    # 2. Check title alignment
    print(f"\n--- Title Alignment Check ---")
    print(f"{'Control ID':>10} | {'ISMS.md (Official English)':55s} | {'JSON (Indonesian)':50s} | Status")
    print(f"{'-'*10}-+-{'-'*55}-+-{'-'*50}-+-{'-'*10}")

    mismatches = []
    for cid in sorted(ISMS_CONTROLS.keys(), key=lambda x: (int(x.split('.')[1]), int(x.split('.')[2]))):
        official = ISMS_CONTROLS[cid]
        our_title = json_map.get(cid, "MISSING")

        # Simple heuristic: check if the Indonesian title seems to match the English concept
        # We flag potential issues for manual review
        status = "OK"

        # Known mapping checks
        checks = {
            "A.5.1": "kebijakan keamanan informasi",
            "A.5.2": ("peninjauan", "peran", "tanggung jawab"),  # Could be either
            "A.5.3": ("pemisahan tugas", "peran"),
            "A.5.4": ("pemisahan tugas", "tanggung jawab manajemen"),
        }

        # Flag if control numbering vs name seems wrong
        # The key check: is A.5.2 = "Roles and Responsibilities" or "Review of policies"?
        if cid == "A.5.1" and "kebijakan" in our_title.lower():
            status = "OK"
        elif cid == "A.5.2" and "peninjauan" in our_title.lower():
            status = "MISMATCH"
            mismatches.append((cid, official, our_title, "A.5.2 should be 'Roles and Responsibilities', not 'Review of policies'"))
        elif cid == "A.5.3" and "pemisahan tugas" in our_title.lower():
            status = "MISMATCH"
            mismatches.append((cid, official, our_title, "A.5.3 should be 'Segregation of Duties', JSON has correct title but ISMS says A.5.3=Segregation"))
            status = "OK"  # Actually this IS correct
        elif cid == "A.5.4" and "pemisahan tugas" in our_title.lower():
            status = "MISMATCH"
            mismatches.append((cid, official, our_title, "A.5.4 should be 'Management Responsibilities', not 'Segregation of Duties'"))

        if our_title == "MISSING":
            status = "MISSING"
            mismatches.append((cid, official, our_title, "Control missing from JSON"))

        print(f"{cid:>10} | {official:55s} | {our_title:50s} | {status}")

    # 3. Detailed mismatch report
    if mismatches:
        print(f"\n{'=' * 90}")
        print(f"MISMATCHES FOUND: {len(mismatches)}")
        print(f"{'=' * 90}")
        for cid, official, ours, reason in mismatches:
            print(f"\n  {cid}:")
            print(f"    ISMS.md (official): {official}")
            print(f"    JSON (ours)       : {ours}")
            print(f"    Issue             : {reason}")
    else:
        print(f"\nNo mismatches detected (manual review recommended for Indonesian translations)")

    # 4. CSV control_id check
    print(f"\n--- CSV Control ID Check ---")
    csv_missing = isms_ids - csv_control_ids
    csv_extra = csv_control_ids - isms_ids

    if csv_missing:
        print(f"Control IDs in ISMS.md but NOT in CSV ({len(csv_missing)}):")
        for cid in sorted(csv_missing):
            print(f"  {cid}")
    else:
        print(f"All ISMS.md control IDs present in CSV: PASS")

    if csv_extra:
        print(f"Control IDs in CSV but NOT in ISMS.md ({len(csv_extra)}):")
        for cid in sorted(csv_extra):
            print(f"  {cid}")
    else:
        print(f"No extra control IDs in CSV: PASS")


if __name__ == "__main__":
    main()
