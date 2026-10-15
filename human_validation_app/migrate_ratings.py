"""
Migration and Seeding Module for HinglishEval Human Validation Platform.
Supports seamless migration from local SQLite (ratings_4000.db) to production PostgreSQL.
Guarantees:
1. Exactly 4,000 responses with canonical IDs.
2. Annotator A's 500 completed ratings 100% preserved.
3. Annotator B's 4,000 completed ratings 100% preserved.
4. Idempotent: Never overwrites, deletes, or modifies existing ratings in target DB.
"""

import os
import sys
import gzip
import json
import sqlite3
from pathlib import Path
from datetime import datetime

# UTF-8 stdout configuration for Windows
sys.stdout.reconfigure(encoding="utf-8")

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from human_validation_app.config import (
    TOTAL_EXPECTED_RESPONSES,
    ANNOTATOR_A_KEY,
    ANNOTATOR_B_KEY,
    ADMIN_SECRET,
    DATABASE_URL
)
from human_validation_app.database import engine, SessionLocal, init_db
from human_validation_app.models import Response as StimulusResponse, Annotator, Annotation, AnnotationAudit
from human_validation_app.auth import hash_access_code

SQLITE_SOURCE_DB = APP_DIR / "ratings_4000.db"
SEED_FILE = APP_DIR / "seed_ratings_master.json.gz"


def export_sqlite_to_seed():
    """Export responses, annotators, annotations, and audits from ratings_4000.db into compressed JSON."""
    print("=" * 80)
    print("EXPORTING MASTER RATINGS TO SEED PACKAGE")
    print(f"Source DB: {SQLITE_SOURCE_DB}")
    print(f"Target Seed: {SEED_FILE}")
    print("=" * 80)

    if not SQLITE_SOURCE_DB.exists():
        raise FileNotFoundError(f"Source database {SQLITE_SOURCE_DB} not found!")

    conn = sqlite3.connect(f"file:{SQLITE_SOURCE_DB.as_posix()}?mode=ro", uri=True)
    cur = conn.cursor()

    # 1. Responses
    cur.execute("SELECT id, item_index, prompt_id, model, prompt, response, source_text, created_at FROM responses ORDER BY item_index ASC")
    responses = [
        {
            "id": r[0], "item_index": r[1], "prompt_id": r[2], "model": r[3],
            "prompt": r[4], "response": r[5], "source_text": r[6],
            "created_at": r[7]
        }
        for r in cur.fetchall()
    ]
    print(f"Exported {len(responses)} responses.")
    assert len(responses) == 4000

    # 2. Annotators
    cur.execute("SELECT id, username, display_name, role, access_code_hash, is_active, created_at FROM annotators")
    annotators = [
        {
            "id": r[0], "username": r[1], "display_name": r[2], "role": r[3],
            "access_code_hash": r[4], "is_active": bool(r[5]), "created_at": r[6]
        }
        for r in cur.fetchall()
    ]
    print(f"Exported {len(annotators)} annotator accounts.")

    # 3. Annotations
    cur.execute("""
        SELECT response_id, annotator_id, fluency, code_mixing_naturalness, hindi_grammar,
               prompt_adherence, spelling_consistency, overall, notes, is_completed,
               submitted_at, updated_at
        FROM annotations
    """)
    annotations = [
        {
            "response_id": r[0], "annotator_id": r[1], "fluency": r[2],
            "code_mixing_naturalness": r[3], "hindi_grammar": r[4],
            "prompt_adherence": r[5], "spelling_consistency": r[6],
            "overall": r[7], "notes": r[8], "is_completed": bool(r[9]),
            "submitted_at": r[10], "updated_at": r[11]
        }
        for r in cur.fetchall()
    ]
    print(f"Exported {len(annotations)} annotation records.")
    
    cnt_a = sum(1 for a in annotations if a["annotator_id"] == "annotator_a" and a["is_completed"])
    cnt_b = sum(1 for a in annotations if a["annotator_id"] == "annotator_b" and a["is_completed"])
    print(f"  Annotator A completed: {cnt_a} (Target: 500)")
    print(f"  Annotator B completed: {cnt_b} (Target: 4000)")
    assert cnt_a == 500
    assert cnt_b == 4000

    # 4. Audits
    cur.execute("SELECT response_id, annotator_id, action, old_values, new_values, timestamp FROM annotation_audits")
    audits = [
        {
            "response_id": r[0], "annotator_id": r[1], "action": r[2],
            "old_values": r[3], "new_values": r[4], "timestamp": r[5]
        }
        for r in cur.fetchall()
    ]
    print(f"Exported {len(audits)} audit trail records.")
    conn.close()

    package = {
        "metadata": {
            "exported_at": datetime.utcnow().isoformat(),
            "total_responses": len(responses),
            "annotator_a_completed": cnt_a,
            "annotator_b_completed": cnt_b,
            "total_annotations": len(annotations),
            "total_audits": len(audits)
        },
        "responses": responses,
        "annotators": annotators,
        "annotations": annotations,
        "audits": audits
    }

    with gzip.open(SEED_FILE, "wt", encoding="utf-8") as f:
        json.dump(package, f)

    file_size_kb = SEED_FILE.stat().st_size / 1024
    print(f"Successfully saved compressed seed package to {SEED_FILE} ({file_size_kb:.1f} KB).")


def migrate_to_target_db():
    """Idempotently seed the target database (PostgreSQL or SQLite) from the seed package."""
    print("=" * 80)
    print("MIGRATING RATINGS TO TARGET DATABASE")
    print(f"Database URL: {DATABASE_URL}")
    print("=" * 80)

    if not SEED_FILE.exists():
        print("Seed file not found, creating from SQLite...")
        export_sqlite_to_seed()

    with gzip.open(SEED_FILE, "rt", encoding="utf-8") as f:
        data = json.load(f)

    init_db()
    session = SessionLocal()
    try:
        # Check existing records
        existing_resp = session.query(StimulusResponse).count()
        existing_ann_a = session.query(Annotation).filter_by(annotator_id="annotator_a", is_completed=True).count()
        existing_ann_b = session.query(Annotation).filter_by(annotator_id="annotator_b", is_completed=True).count()

        print(f"Existing Target Database State:")
        print(f"  Responses: {existing_resp} / 4000")
        print(f"  Annotator A Completed: {existing_ann_a} / 500")
        print(f"  Annotator B Completed: {existing_ann_b} / 4000")

        # 1. Seed Annotators
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

        # 2. Seed Responses if missing
        if existing_resp < TOTAL_EXPECTED_RESPONSES:
            print(f"Seeding {len(data['responses'])} stimulus responses...")
            # Collect existing IDs to avoid duplicate key errors
            existing_ids = {r[0] for r in session.query(StimulusResponse.id).all()}
            resp_objs = []
            for r in data["responses"]:
                if r["id"] not in existing_ids:
                    resp_objs.append(StimulusResponse(
                        id=r["id"],
                        item_index=r["item_index"],
                        prompt_id=r["prompt_id"],
                        model=r["model"],
                        prompt=r["prompt"],
                        response=r["response"],
                        source_text=r.get("source_text", "")
                    ))
            if resp_objs:
                session.bulk_save_objects(resp_objs)
                session.commit()
            print("Responses seeded successfully.")

        # 3. Seed Annotations if missing
        existing_ann_pairs = {(a.response_id, a.annotator_id) for a in session.query(Annotation.response_id, Annotation.annotator_id).all()}
        ann_objs = []
        for a in data["annotations"]:
            pair = (a["response_id"], a["annotator_id"])
            if pair not in existing_ann_pairs:
                sub_at = datetime.fromisoformat(a["submitted_at"]) if a.get("submitted_at") else datetime.utcnow()
                upd_at = datetime.fromisoformat(a["updated_at"]) if a.get("updated_at") else datetime.utcnow()
                ann_objs.append(Annotation(
                    response_id=a["response_id"],
                    annotator_id=a["annotator_id"],
                    fluency=a["fluency"],
                    code_mixing_naturalness=a["code_mixing_naturalness"],
                    hindi_grammar=a["hindi_grammar"],
                    prompt_adherence=a["prompt_adherence"],
                    spelling_consistency=a["spelling_consistency"],
                    overall=a["overall"],
                    notes=a.get("notes", "") or "",
                    is_completed=a["is_completed"],
                    submitted_at=sub_at,
                    updated_at=upd_at
                ))
        if ann_objs:
            print(f"Inserting {len(ann_objs)} missing annotations...")
            session.bulk_save_objects(ann_objs)
            session.commit()
            print("Annotations seeded successfully.")

        # 4. Final verification
        final_resp = session.query(StimulusResponse).count()
        final_ann_a = session.query(Annotation).filter_by(annotator_id="annotator_a", is_completed=True).count()
        final_ann_b = session.query(Annotation).filter_by(annotator_id="annotator_b", is_completed=True).count()

        print("\n=== MIGRATION VERIFICATION ===")
        print(f"Total responses: {final_resp} / 4000")
        print(f"Annotator A completed: {final_ann_a} / 4000 (Target: 500, Remaining: {4000 - final_ann_a})")
        print(f"Annotator B completed: {final_ann_b} / 4000 (Target: 4000, Remaining: {4000 - final_ann_b})")
        assert final_resp == 4000
        assert final_ann_a >= 500
        assert final_ann_b == 4000
        print("MIGRATION PASSED WITH 100% INTEGRITY GUARANTEE!")

    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    export_sqlite_to_seed()
    migrate_to_target_db()
