"""
Sync and Preserve Script for HinglishEval 4,000 Human Validation App.
Guarantees:
1. Exactly 4,000 responses with preserved canonical response IDs (RESP_{model}_{row_index:04d}).
2. Items 1..500 map to Annotator A's 500 evaluated responses.
3. Items 501..4000 map to the remaining 3,500 benchmark responses.
4. Annotator A's 500 completed ratings (with all 6 scores, notes, timestamps) are 100% preserved.
5. Annotator B starts at exactly 0/4,000 completed ratings.
6. Annotator accounts (Annotator A, Annotator B, Admin) are verified.
"""

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 stdout on Windows
sys.stdout.reconfigure(encoding="utf-8")

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from human_validation_app.database import engine, SessionLocal, init_db
from human_validation_app.models import Response as StimulusResponse, Annotator, Annotation, AnnotationAudit
from human_validation_app.auth import hash_access_code
from human_validation_app.config import ANNOTATOR_A_KEY, ANNOTATOR_B_KEY, ADMIN_SECRET

ORIGINAL_RATINGS_DB = PROJECT_ROOT / "research_upgrade" / "human_validation" / "ratings.db"
GENERATIONS_CSV = PROJECT_ROOT / "outputs" / "controlled_1000" / "benchmark_generations_.csv"
BENCHMARK_CSV = PROJECT_ROOT / "data" / "benchmarks" / "hinglish_bench_.csv"


def sync_responses_and_preserve_a():
    print("=" * 80)
    print("SYNC AND PRESERVE: 4,000 RESPONSES & ANNOTATOR A's 500 RATINGS")
    print("=" * 80)

    # 1. Load source files
    df_gen = pd.read_csv(GENERATIONS_CSV)
    df_gen["response_id"] = df_gen.apply(lambda r: f"RESP_{r['model']}_{r['row_index']:04d}", axis=1)

    df_bench = pd.read_csv(BENCHMARK_CSV)
    bench_lookup = {}
    for _, row in df_bench.iterrows():
        p_id = int(row["prompt_id"])
        bench_lookup[p_id] = {
            "source_text": str(row["source_text"]) if pd.notnull(row["source_text"]) else ""
        }

    # 2. Load Annotator A's 500 completed records from ratings.db
    conn_orig = sqlite3.connect(ORIGINAL_RATINGS_DB)
    df_orig_ratings_a = pd.read_sql_query("""
        SELECT r.*, a.item_index as assign_item_index, a.prompt_id, a.model, a.prompt, a.response, a.source_text
        FROM ratings r
        JOIN assignments a ON r.response_id = a.response_id
        WHERE r.annotator_id='annotator_a'
        ORDER BY a.item_index ASC;
    """, conn_orig)
    conn_orig.close()

    print(f"Loaded {len(df_orig_ratings_a)} completed ratings for Annotator A from original ratings.db.")
    assert len(df_orig_ratings_a) == 500, f"Expected 500 ratings, found {len(df_orig_ratings_a)}"

    # 3. Create the 4,000 ordered stimulus list
    # Items 1..500: Annotator A's 500 responses
    ordered_items = []
    seen_response_ids = set()

    for idx, r in df_orig_ratings_a.iterrows():
        item_idx = int(r["assign_item_index"])
        resp_id = str(r["response_id"])
        seen_response_ids.add(resp_id)
        ordered_items.append({
            "id": resp_id,
            "item_index": item_idx,
            "prompt_id": int(r["prompt_id"]),
            "model": str(r["model"]),
            "prompt": str(r["prompt"]),
            "response": str(r["response"]),
            "source_text": str(r["source_text"]) if pd.notnull(r["source_text"]) else ""
        })

    # Items 501..4000: The remaining 3,500 responses from benchmark generations
    remaining_gen = df_gen[~df_gen["response_id"].isin(seen_response_ids)].copy()
    remaining_gen = remaining_gen.sort_values(by=["row_index", "model"]).reset_index(drop=True)

    print(f"Adding {len(remaining_gen)} remaining responses to reach 4,000 total.")
    current_item_index = 501
    for _, r in remaining_gen.iterrows():
        resp_id = str(r["response_id"])
        p_id = int(r["row_index"]) + 1
        s_text = bench_lookup.get(p_id, {}).get("source_text", "")
        ordered_items.append({
            "id": resp_id,
            "item_index": current_item_index,
            "prompt_id": p_id,
            "model": str(r["model"]),
            "prompt": str(r["prompt"]),
            "response": str(r["response"]),
            "source_text": s_text
        })
        current_item_index += 1

    assert len(ordered_items) == 4000, f"Expected 4000 items, got {len(ordered_items)}"
    print(f"Successfully generated 4,000 ordered stimulus items.")

    # 4. Insert or update into database
    init_db()
    session = SessionLocal()
    try:
        # Seed annotator accounts
        annotators_config = [
            {"id": "annotator_a", "username": "annotator_a", "display_name": "Annotator A (Lead)", "role": "annotator", "key": ANNOTATOR_A_KEY},
            {"id": "annotator_b", "username": "annotator_b", "display_name": "Annotator B (Partner)", "role": "annotator", "key": ANNOTATOR_B_KEY},
            {"id": "admin", "username": "admin", "display_name": "Project Lead (Admin)", "role": "admin", "key": ADMIN_SECRET}
        ]
        for cfg in annotators_config:
            existing = session.query(Annotator).filter_by(id=cfg["id"]).first()
            hashed = hash_access_code(cfg["key"])
            if not existing:
                session.add(Annotator(
                    id=cfg["id"],
                    username=cfg["username"],
                    display_name=cfg["display_name"],
                    role=cfg["role"],
                    access_code_hash=hashed,
                    is_active=True
                ))
            else:
                existing.display_name = cfg["display_name"]
                existing.access_code_hash = hashed
                existing.is_active = True
        session.commit()

        # Clean responses and annotations cleanly in new app DB (ratings_4000.db)
        print("Synchronizing responses table in ratings_4000.db...")
        session.query(AnnotationAudit).delete()
        session.query(Annotation).delete()
        session.query(StimulusResponse).delete()
        session.commit()

        # Batch insert 4,000 responses
        resp_objects = [
            StimulusResponse(
                id=item["id"],
                item_index=item["item_index"],
                prompt_id=item["prompt_id"],
                model=item["model"],
                prompt=item["prompt"],
                response=item["response"],
                source_text=item["source_text"]
            )
            for item in ordered_items
        ]
        session.bulk_save_objects(resp_objects)
        session.commit()
        print(f"Inserted 4,000 stimulus responses into database.")

        # 5. Insert Annotator A's 500 completed ratings
        print("Inserting Annotator A's 500 completed ratings...")
        ann_objects = []
        for _, r in df_orig_ratings_a.iterrows():
            sub_at = datetime.fromisoformat(str(r["submitted_at"])) if pd.notnull(r["submitted_at"]) else datetime.utcnow()
            upd_at = datetime.fromisoformat(str(r["updated_at"])) if pd.notnull(r["updated_at"]) else datetime.utcnow()
            ann_obj = Annotation(
                response_id=str(r["response_id"]),
                annotator_id="annotator_a",
                fluency=int(r["fluency"]),
                code_mixing_naturalness=int(r["code_mixing_naturalness"]),
                hindi_grammar=int(r["hindi_grammar"]),
                prompt_adherence=int(r["prompt_adherence"]),
                spelling_consistency=int(r["spelling_consistency"]),
                overall=int(r["overall"]),
                notes=str(r["notes"]) if pd.notnull(r["notes"]) else "",
                is_completed=True,
                submitted_at=sub_at,
                updated_at=upd_at
            )
            ann_objects.append(ann_obj)

        session.bulk_save_objects(ann_objects)
        session.commit()
        print("Annotator A's 500 ratings successfully committed!")

        # Verify counts in database
        total_resp = session.query(StimulusResponse).count()
        total_ann_a = session.query(Annotation).filter_by(annotator_id="annotator_a", is_completed=True).count()
        total_ann_b = session.query(Annotation).filter_by(annotator_id="annotator_b").count()

        print("\n=== FINAL DATABASE VERIFICATION ===")
        print(f"Total responses in database: {total_resp} / 4000")
        print(f"Annotator A completed ratings: {total_ann_a} / 4000 (Target: 500)")
        print(f"Annotator B completed ratings: {total_ann_b} / 4000 (Target: 0)")
        assert total_resp == 4000
        assert total_ann_a == 500
        assert total_ann_b == 0
        print("Verification PASSED!")

    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    sync_responses_and_preserve_a()
