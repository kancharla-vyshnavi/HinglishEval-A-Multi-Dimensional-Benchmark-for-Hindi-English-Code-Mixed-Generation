"""
import_csv_ratings.py
Validates and imports a completed CSV rating sheet into ratings.db,
and regenerates the combined human evaluation dataset and report.

Usage:
  python import_csv_ratings.py --file annotator_B_rating_sheet.csv --annotator annotator_b
"""

import os
import sys
import argparse
import pandas as pd
import datetime
import sqlite3
import json

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "ratings.db")
MANIFEST_CSV = os.path.join(BASE_DIR, "assignment_manifest.csv")

DIMS = ["fluency", "code_mixing_naturalness", "hindi_grammar", "prompt_adherence", "spelling_consistency", "overall"]

def import_csv(file_path: str, annotator_id: str):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    if annotator_id not in ["annotator_a", "annotator_b"]:
        raise ValueError("annotator_id must be 'annotator_a' or 'annotator_b'")

    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} rows from {file_path}")

    # Column mapping
    col_map = {
        "fluency_1_to_5": "fluency",
        "code_mixing_naturalness_1_to_5": "code_mixing_naturalness",
        "hindi_grammar_1_to_5": "hindi_grammar",
        "prompt_adherence_1_to_5": "prompt_adherence",
        "spelling_consistency_1_to_5": "spelling_consistency",
        "overall_1_to_5": "overall",
        "fluency": "fluency",
        "code_mixing_naturalness": "code_mixing_naturalness",
        "hindi_grammar": "hindi_grammar",
        "prompt_adherence": "prompt_adherence",
        "spelling_consistency": "spelling_consistency",
        "overall": "overall",
        "notes": "notes"
    }

    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row

    imported = 0
    updated = 0
    skipped_empty = 0
    errors = []

    try:
        with conn:
            for idx, r in df.iterrows():
                assign_id = str(r["assignment_id"]).strip()
                cur_a = conn.execute(
                    "SELECT response_id, annotator_id FROM assignments WHERE assignment_id = ?;",
                    (assign_id,)
                )
                a_row = cur_a.fetchone()
                if not a_row:
                    errors.append(f"Row {idx+1}: Assignment ID '{assign_id}' not found in manifest.")
                    continue
                if a_row["annotator_id"] != annotator_id:
                    errors.append(f"Row {idx+1}: Assignment '{assign_id}' does not belong to {annotator_id}.")
                    continue

                resp_id = a_row["response_id"]

                # Extract scores
                scores = {}
                is_filled = True
                for target_dim in DIMS:
                    val = None
                    for possible_col, dim_name in col_map.items():
                        if dim_name == target_dim and possible_col in r and pd.notna(r[possible_col]) and str(r[possible_col]).strip() != "":
                            try:
                                val = int(float(r[possible_col]))
                            except ValueError:
                                pass
                            break
                    if val is None:
                        is_filled = False
                        break
                    if val < 1 or val > 5:
                        errors.append(f"Row {idx+1} ({assign_id}): Invalid score {val} for {target_dim}. Must be 1-5.")
                        is_filled = False
                        break
                    scores[target_dim] = val

                if not is_filled:
                    skipped_empty += 1
                    continue

                notes_val = str(r.get("notes", "")) if pd.notna(r.get("notes", "")) else ""
                now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

                cur_exist = conn.execute("SELECT * FROM ratings WHERE response_id = ?;", (resp_id,))
                exist = cur_exist.fetchone()

                if exist:
                    conn.execute("""
                        UPDATE ratings SET
                            fluency = ?, code_mixing_naturalness = ?, hindi_grammar = ?,
                            prompt_adherence = ?, spelling_consistency = ?, overall = ?,
                            notes = ?, updated_at = ?, assignment_status = 'updated'
                        WHERE response_id = ?;
                    """, (
                        scores["fluency"], scores["code_mixing_naturalness"], scores["hindi_grammar"],
                        scores["prompt_adherence"], scores["spelling_consistency"], scores["overall"],
                        notes_val, now_iso, resp_id
                    ))
                    updated += 1
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
                        scores["fluency"], scores["code_mixing_naturalness"], scores["hindi_grammar"],
                        scores["prompt_adherence"], scores["spelling_consistency"], scores["overall"],
                        notes_val, now_iso, now_iso
                    ))
                    imported += 1

                conn.execute("""
                    INSERT INTO ratings_audit_trail (response_id, annotator_id, action, old_values, new_values, timestamp)
                    VALUES (?, ?, 'CSV_IMPORT', NULL, ?, ?);
                """, (resp_id, annotator_id, json.dumps(scores), now_iso))

        print(f"\nImport Summary for {annotator_id}:")
        print(f"  New ratings saved: {imported}")
        print(f"  Ratings updated:   {updated}")
        print(f"  Empty / unrated:   {skipped_empty}")
        if errors:
            print(f"  Validation Errors ({len(errors)}):")
            for e in errors[:5]:
                print(f"    - {e}")

        # Regenerate combined dataset
        import combine_and_validate_ratings
        combine_and_validate_ratings.combine_and_validate()
        print("\nUpdated combined human ratings exports successfully.")
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import CSV rating sheet into project database")
    parser.add_argument("--file", required=True, help="Path to completed CSV file")
    parser.add_argument("--annotator", required=True, choices=["annotator_a", "annotator_b"], help="Annotator ID")
    args = parser.parse_args()
    import_csv(args.file, args.annotator)
