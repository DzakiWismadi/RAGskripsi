"""
validate_data.py
Validates iso_controls.json and audit_gold_standard.csv integrity.
"""

import json
import csv
import os
import sys
from collections import Counter

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
CONTROLS_PATH = os.path.join(DATA_DIR, "iso_controls.json")
GOLD_STANDARD_PATH = os.path.join(DATA_DIR, "audit_gold_standard.csv")

REQUIRED_CONTROL_FIELDS = ["control_id", "title", "objective", "description", "implementation_guidance"]
VALID_APPLICABLE = {"Yes", "No"}
VALID_STATUS = {"Implemented", "Not Implemented", "Partially Implemented"}


def validate_controls():
    print("=" * 60)
    print("Validating iso_controls.json")
    print("=" * 60)

    with open(CONTROLS_PATH, "r", encoding="utf-8") as f:
        controls = json.load(f)

    errors = []

    # Check count
    if len(controls) != 93:
        errors.append(f"Expected 93 controls, found {len(controls)}")

    # Check required fields and non-empty
    control_ids = []
    for i, ctrl in enumerate(controls):
        for field in REQUIRED_CONTROL_FIELDS:
            if field not in ctrl:
                errors.append(f"Control #{i}: missing field '{field}'")
            elif not ctrl[field] or not ctrl[field].strip():
                errors.append(f"Control #{i} ({ctrl.get('control_id', '?')}): empty field '{field}'")
        control_ids.append(ctrl.get("control_id", ""))

    # Check duplicates
    id_counts = Counter(control_ids)
    for cid, count in id_counts.items():
        if count > 1:
            errors.append(f"Duplicate control_id: {cid} (appears {count} times)")

    # Check description word count
    short_descriptions = []
    for ctrl in controls:
        desc = ctrl.get("description", "")
        word_count = len(desc.split())
        if word_count < 50:
            short_descriptions.append(f"  {ctrl['control_id']}: {word_count} words")

    # Distribution by category
    category_counts = Counter()
    for ctrl in controls:
        cat = ctrl["control_id"].rsplit(".", 1)[0]
        category_counts[cat] += 1

    # Print results
    print(f"Total controls: {len(controls)}")
    print(f"Category distribution:")
    for cat in sorted(category_counts):
        print(f"  {cat}: {category_counts[cat]}")

    if short_descriptions:
        print(f"\nWARNING: {len(short_descriptions)} controls have description < 50 words:")
        for s in short_descriptions:
            print(s)

    if errors:
        print(f"\nFAIL: {len(errors)} errors found:")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        print("\nPASS: iso_controls.json is valid")
        return True


def validate_gold_standard():
    print("\n" + "=" * 60)
    print("Validating audit_gold_standard.csv")
    print("=" * 60)

    # Load valid control IDs
    with open(CONTROLS_PATH, "r", encoding="utf-8") as f:
        controls = json.load(f)
    valid_control_ids = {ctrl["control_id"] for ctrl in controls}

    with open(GOLD_STANDARD_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    errors = []

    # Check minimum rows
    if len(rows) < 100:
        errors.append(f"Expected 100+ rows, found {len(rows)}")

    # Check required columns
    required_cols = {"sentence", "control_id", "applicable", "implementation_status", "justification"}
    if rows:
        actual_cols = set(rows[0].keys())
        missing_cols = required_cols - actual_cols
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")

    # Validate each row
    control_id_set = set()
    status_counts = Counter()
    applicable_counts = Counter()
    category_counts = Counter()

    for i, row in enumerate(rows, 1):
        cid = row.get("control_id", "").strip()
        applicable = row.get("applicable", "").strip()
        status = row.get("implementation_status", "").strip()
        sentence = row.get("sentence", "").strip()
        justification = row.get("justification", "").strip()

        if not sentence:
            errors.append(f"Row {i}: empty sentence")
        if not justification:
            errors.append(f"Row {i}: empty justification")

        if cid not in valid_control_ids:
            errors.append(f"Row {i}: invalid control_id '{cid}'")
        else:
            control_id_set.add(cid)
            cat = cid.rsplit(".", 1)[0]
            category_counts[cat] += 1

        if applicable not in VALID_APPLICABLE:
            errors.append(f"Row {i}: invalid applicable '{applicable}' (expected {VALID_APPLICABLE})")
        applicable_counts[applicable] += 1

        if status not in VALID_STATUS:
            errors.append(f"Row {i}: invalid implementation_status '{status}' (expected {VALID_STATUS})")
        status_counts[status] += 1

    # Check distribution requirements
    if len(control_id_set) < 20:
        errors.append(f"Expected 20+ distinct control IDs, found {len(control_id_set)}")

    no_count = applicable_counts.get("No", 0)
    if no_count < 5:
        errors.append(f"Expected 5+ applicable=No rows, found {no_count}")

    if len(status_counts) < 3:
        errors.append(f"Expected all 3 status values, found {list(status_counts.keys())}")

    # Print results
    print(f"Total rows: {len(rows)}")
    print(f"Distinct control IDs: {len(control_id_set)}")
    print(f"\nCategory distribution:")
    for cat in sorted(category_counts):
        print(f"  {cat}: {category_counts[cat]}")
    print(f"\nApplicable distribution:")
    for val, count in sorted(applicable_counts.items()):
        print(f"  {val}: {count}")
    print(f"\nImplementation status distribution:")
    for val, count in sorted(status_counts.items()):
        print(f"  {val}: {count}")

    if errors:
        print(f"\nFAIL: {len(errors)} errors found:")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        print("\nPASS: audit_gold_standard.csv is valid")
        return True


if __name__ == "__main__":
    ok1 = validate_controls()
    ok2 = validate_gold_standard()

    print("\n" + "=" * 60)
    if ok1 and ok2:
        print("ALL VALIDATIONS PASSED")
    else:
        print("SOME VALIDATIONS FAILED")
        sys.exit(1)
