"""
Idempotent import script for HinglishEval 4,000 generated responses.
Preserves Annotator A's 500 completed ratings, loads all 4,000 responses with
canonical response IDs (RESP_{model}_{row_index:04d}), seeds annotators,
and ensures Annotator B starts cleanly at 0/4,000.
"""

import os
import sys
from pathlib import Path
import sqlite3
import pandas as pd
from datetime import datetime

# UTF-8 stdout configuration for Windows
sys.stdout.reconfigure(encoding="utf-8")

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from human_validation_app.config import (
    DEFAULT_GENERATIONS_CSV,
    DEFAULT_BENCHMARK_CSV,
    TOTAL_EXPECTED_RESPONSES,
    EXPECTED_MODELS,
    ANNOTATOR_A_KEY,
    ANNOTATOR_B_KEY,
    ADMIN_SECRET
)
from human_validation_app.database import engine, SessionLocal, init_db
from human_validation_app.models import Response as StimulusResponse, Annotator, Annotation
from human_validation_app.auth import hash_access_code

ORIGINAL_RATINGS_DB = PROJECT_ROOT / "research_upgrade" / "human_validation" / "ratings.db"


def seed_annotators(session):
    """Seed or update Annotator accounts."""
    annotators_config = [
        {"id": "annotator_a", "username": "annotator_a", "display_name": "Annotator A (Lead)", "role": "annotator", "key": ANNOTATOR_A_KEY},
        {"id": "annotator_b", "username": "annotator_b", "display_name": "Annotator B (Partner)", "role": "annotator", "key": ANNOTATOR_B_KEY},
        {"id": "admin", "username": "admin", "display_name": "Project Lead (Admin)", "role": "admin", "key": ADMIN_SECRET}
    ]

    for cfg in annotators_config:
        existing = session.query(Annotator).filter_by(id=cfg["id"]).first()
        hashed = hash_access_code(cfg["key"])
        if not existing:
            user = Annotator(
                id=cfg["id"],
                username=cfg["username"],
                display_name=cfg["display_name"],
                role=cfg["role"],
                access_code_hash=hashed,
                is_active=True
            )
            session.add(user)
        else:
            existing.display_name = cfg["display_name"]
            existing.access_code_hash = hashed
            existing.is_active = True
    session.commit()


def import_responses():
    """
    Import 4,000 responses into the database idempotently while preserving
    Annotator A's 500 completed ratings and keeping Annotator B at 0/4000.
    """
    init_db()
    session = SessionLocal()
    try:
        seed_annotators(session)

        resp_count = session.query(StimulusResponse).count()
        ann_a_count = session.query(Annotation).filter_by(annotator_id="annotator_a", is_completed=True).count()

        if resp_count == TOTAL_EXPECTED_RESPONSES and ann_a_count == 500:
            print(f"Database already contains {resp_count} responses and {ann_a_count} preserved ratings for Annotator A.")
            print("Skipping re-import to preserve existing evaluation state.")
            return resp_count

        # Otherwise run migrate_to_target_db to preserve Annotator A (500) and Annotator B (4,000)
        from human_validation_app.migrate_ratings import migrate_to_target_db
        migrate_to_target_db()
        return TOTAL_EXPECTED_RESPONSES
    finally:
        session.close()


if __name__ == "__main__":
    import_responses()
