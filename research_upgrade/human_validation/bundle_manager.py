"""
bundle_manager.py
Provides export and import utilities for offline/air-gapped human rating bundles.
Ensures zero data loss, strict schema validation, and complete audit tracking
if Annotator B ever operates in an offline environment or sends rating batches.
"""

import os
import sys
import json
import sqlite3
import hashlib
import datetime
import argparse
from typing import Dict, Any, List

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "ratings.db")
MANIFEST_CSV = os.path.join(BASE_DIR, "assignment_manifest.csv")

DIMS = ["fluency", "code_mixing_naturalness", "hindi_grammar", "prompt_adherence", "spelling_consistency", "overall"]

def export_bundle(annotator_id: str, output_path: str = None) -> str:
    if annotator_id not in ["annotator_a", "annotator_b"]:
        raise ValueError("annotator_id must be 'annotator_a' or 'annotator_b'")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute("""
            SELECT response_id, assignment_id, annotator_id,
                   fluency, code_mixing_naturalness, hindi_grammar,
                   prompt_adherence, spelling_consistency, overall,
                   notes, submitted_at, updated_at, assignment_status
            FROM ratings
            WHERE annotator_id = ?
            ORDER BY assignment_id ASC;
        """, (annotator_id,))
        rows = [dict(r) for r in cur.fetchall()]
        
        bundle = {
            "version": "1.0",
            "annotator_id": annotator_id,
            "export_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "record_count": len(rows),
            "records": rows
        }

        # Compute hash
        bundle_json = json.dumps(bundle, indent=2, ensure_ascii=False)
        sha256 = hashlib.sha256(bundle_json.encode("utf-8")).hexdigest()
        bundle["sha256"] = sha256

        if not output_path:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(BASE_DIR, f"ratings_bundle_{annotator_id}_{ts}.json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(bundle, f, indent=2, ensure_ascii=False)

        print(f"Exported {len(rows)} ratings for {annotator_id} to: {output_path}")
        return output_path
    finally:
        conn.close()

def import_bundle(bundle_path: str) -> Dict[str, Any]:
    if not os.path.exists(bundle_path):
        raise FileNotFoundError(f"Bundle file not found: {bundle_path}")

    with open(bundle_path, "r", encoding="utf-8") as f:
        bundle = json.load(f)

    annotator_id = bundle.get("annotator_id")
    records = bundle.get("records", [])

    print(f"Importing {len(records)} records for '{annotator_id}' from {bundle_path}...")

    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    imported_count = 0
    updated_count = 0
    invalid_count = 0

    try:
        with conn:
            for rec in records:
                resp_id = rec.get("response_id")
                assign_id = rec.get("assignment_id")
                
                # Check assignment validity in manifest
                cur_a = conn.execute(
                    "SELECT annotator_id FROM assignments WHERE assignment_id = ? AND response_id = ?;",
                    (assign_id, resp_id)
                )
                a_row = cur_a.fetchone()
                if not a_row or a_row["annotator_id"] != annotator_id:
                    print(f"Skipping record {assign_id} - ownership/ID mismatch.")
                    invalid_count += 1
                    continue

                # Check scores
                valid_scores = True
                for dim in DIMS:
                    val = rec.get(dim)
                    if not isinstance(val, int) or val < 1 or val > 5:
                        valid_scores = False
                        break
                
                if not valid_scores:
                    print(f"Skipping record {assign_id} - scores not in 1-5 integer range.")
                    invalid_count += 1
                    continue

                # Upsert
                cur_exist = conn.execute("SELECT * FROM ratings WHERE response_id = ?;", (resp_id,))
                exist = cur_exist.fetchone()

                now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
                submitted_at = rec.get("submitted_at") or now_iso
                updated_at = rec.get("updated_at") or now_iso

                if exist:
                    conn.execute("""
                        UPDATE ratings SET
                            fluency = ?, code_mixing_naturalness = ?, hindi_grammar = ?,
                            prompt_adherence = ?, spelling_consistency = ?, overall = ?,
                            notes = ?, updated_at = ?, assignment_status = 'updated'
                        WHERE response_id = ?;
                    """, (
                        rec["fluency"], rec["code_mixing_naturalness"], rec["hindi_grammar"],
                        rec["prompt_adherence"], rec["spelling_consistency"], rec["overall"],
                        rec.get("notes", ""), updated_at, resp_id
                    ))
                    updated_count += 1
                else:
                    conn.execute("""
                        INSERT INTO ratings (
                            response_id, assignment_id, annotator_id,
                            fluency, code_mixing_naturalness, hindi_grammar,
                            prompt_adherence, spelling_consistency, overall,
                            notes, submitted_at, updated_at, assignment_status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'completed');
                    """, (
                        resp_id, assign_id, annotator_id,
                        rec["fluency"], rec["code_mixing_naturalness"], rec["hindi_grammar"],
                        rec["prompt_adherence"], rec["spelling_consistency"], rec["overall"],
                        rec.get("notes", ""), submitted_at, updated_at
                    ))
                    imported_count += 1

                # Audit trail
                conn.execute("""
                    INSERT INTO ratings_audit_trail (response_id, annotator_id, action, old_values, new_values, timestamp)
                    VALUES (?, ?, 'BUNDLE_IMPORT', NULL, ?, ?);
                """, (resp_id, annotator_id, json.dumps({d: rec[d] for d in DIMS}), now_iso))

        print(f"Import complete: {imported_count} new inserted, {updated_count} updated, {invalid_count} rejected.")

        # Re-run combined export
        import combine_and_validate_ratings
        combine_and_validate_ratings.combine_and_validate()

        return {
            "imported_count": imported_count,
            "updated_count": updated_count,
            "invalid_count": invalid_count
        }
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HinglishEval Human Rating Bundle Manager")
    parser.add_argument("--action", choices=["export", "import"], required=True)
    parser.add_argument("--annotator", choices=["annotator_a", "annotator_b"], default="annotator_b")
    parser.add_argument("--file", type=str, help="Path to bundle JSON file")

    args = parser.parse_args()
    if args.action == "export":
        export_bundle(args.annotator, args.file)
    elif args.action == "import":
        if not args.file:
            print("Error: --file argument is required for import action.")
            sys.exit(1)
        import_bundle(args.file)
