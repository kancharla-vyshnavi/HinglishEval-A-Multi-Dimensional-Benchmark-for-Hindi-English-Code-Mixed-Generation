"""
db.py
SQLite persistent storage engine for HinglishEval human evaluation.
Features:
- WAL mode for concurrent reading and writing
- Strict schema validation
- ACID transactions and atomic updates
- Complete audit trail for score modifications
"""

import os
import sqlite3
import json
import datetime
from typing import Dict, Any, List, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(__file__), "ratings.db")
MANIFEST_CSV = os.path.join(os.path.dirname(__file__), "assignment_manifest.csv")

# Predefined secure access tokens
TOKENS = {
    "eval_a_lead_2026": {"annotator_id": "annotator_a", "role": "annotator", "name": "Annotator A (Lead)"},
    "eval_b_partner_2026": {"annotator_id": "annotator_b", "role": "annotator", "name": "Annotator B (Partner)"},
    "admin_hinglish_eval_master": {"annotator_id": "admin", "role": "admin", "name": "Project Lead (Admin)"}
}

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_db(force_reload_manifest: bool = False):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    with conn:
        if force_reload_manifest:
            conn.execute("DROP TABLE IF EXISTS assignments;")

        conn.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            assignment_id TEXT PRIMARY KEY,
            annotator_id TEXT NOT NULL,
            item_index INTEGER NOT NULL,
            response_id TEXT NOT NULL,
            global_row_index INTEGER NOT NULL,
            row_index INTEGER NOT NULL,
            prompt_id INTEGER NOT NULL,
            model TEXT NOT NULL,
            category TEXT NOT NULL,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL,
            source_text TEXT
        );
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            response_id TEXT PRIMARY KEY,
            assignment_id TEXT NOT NULL,
            annotator_id TEXT NOT NULL,
            fluency INTEGER NOT NULL,
            code_mixing_naturalness INTEGER NOT NULL,
            hindi_grammar INTEGER NOT NULL,
            prompt_adherence INTEGER NOT NULL,
            spelling_consistency INTEGER NOT NULL,
            overall INTEGER NOT NULL,
            notes TEXT,
            submitted_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            assignment_status TEXT NOT NULL,
            FOREIGN KEY (assignment_id) REFERENCES assignments (assignment_id)
        );
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS ratings_audit_trail (
            audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            response_id TEXT NOT NULL,
            annotator_id TEXT NOT NULL,
            action TEXT NOT NULL,
            old_values TEXT,
            new_values TEXT,
            timestamp TEXT NOT NULL
        );
        """)

        conn.execute("CREATE INDEX IF NOT EXISTS idx_assignments_annotator ON assignments(annotator_id, item_index);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ratings_annotator ON ratings(annotator_id);")

        # Reload assignments from manifest if requested or if counts differ
        cursor = conn.execute("SELECT COUNT(*) as count FROM assignments;")
        count = cursor.fetchone()["count"]
        if (count != 1000 or force_reload_manifest) and os.path.exists(MANIFEST_CSV):
            import pandas as pd
            df = pd.read_csv(MANIFEST_CSV)
            conn.execute("DELETE FROM assignments;")
            rows = []
            for _, r in df.iterrows():
                rows.append((
                    str(r["assignment_id"]),
                    str(r["annotator_id"]),
                    int(r["item_index"]),
                    str(r["response_id"]),
                    int(r["global_row_index"]),
                    int(r["row_index"]),
                    int(r["prompt_id"]),
                    str(r["model"]),
                    str(r.get("category", "Casual Conversation")),
                    str(r["prompt"]),
                    str(r["response"]),
                    str(r.get("source_text", ""))
                ))
            conn.executemany("""
            INSERT OR REPLACE INTO assignments (
                assignment_id, annotator_id, item_index, response_id,
                global_row_index, row_index, prompt_id, model, category, prompt, response, source_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, rows)
            print(f"Populated {len(rows)} assignments into SQLite database.")
    conn.close()

def authenticate_token(token: str) -> Optional[Dict[str, str]]:
    if not token:
        return None
    token = token.strip()
    return TOKENS.get(token)

def get_annotator_progress(annotator_id: str) -> Dict[str, Any]:
    conn = get_connection()
    try:
        cur_total = conn.execute("SELECT COUNT(*) as c FROM assignments WHERE annotator_id = ?;", (annotator_id,))
        total = cur_total.fetchone()["c"]

        cur_done = conn.execute("SELECT COUNT(*) as c FROM ratings WHERE annotator_id = ?;", (annotator_id,))
        done = cur_done.fetchone()["c"]

        pct = (done / total * 100.0) if total > 0 else 0.0
        return {
            "annotator_id": annotator_id,
            "total_assigned": total,
            "total_completed": done,
            "remaining": total - done,
            "completion_percentage": round(pct, 2)
        }
    finally:
        conn.close()

def get_assignment_item(annotator_id: str, item_index: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    try:
        cursor = conn.execute("""
            SELECT a.assignment_id, a.item_index, a.category, a.prompt, a.response, a.source_text,
                   r.fluency, r.code_mixing_naturalness, r.hindi_grammar,
                   r.prompt_adherence, r.spelling_consistency, r.overall,
                   r.notes, r.submitted_at, r.updated_at, r.assignment_status
            FROM assignments a
            LEFT JOIN ratings r ON a.response_id = r.response_id
            WHERE a.annotator_id = ? AND a.item_index = ?;
        """, (annotator_id, item_index))
        row = cursor.fetchone()
        if not row:
            return None
        
        # Blinded representation: NO model name, NO model-bearing identifiers leaked!
        return {
            "assignment_id": row["assignment_id"],
            "item_index": row["item_index"],
            "category": row["category"],
            "prompt": row["prompt"],
            "response": row["response"],
            "source_text": row["source_text"],
            "is_rated": row["assignment_status"] is not None,
            "current_ratings": {
                "fluency": row["fluency"],
                "code_mixing_naturalness": row["code_mixing_naturalness"],
                "hindi_grammar": row["hindi_grammar"],
                "prompt_adherence": row["prompt_adherence"],
                "spelling_consistency": row["spelling_consistency"],
                "overall": row["overall"],
                "notes": row["notes"] or ""
            } if row["assignment_status"] is not None else None,
            "last_updated": row["updated_at"]
        }
    finally:
        conn.close()

def get_next_unanswered_index(annotator_id: str, current_index: int = 1) -> int:
    conn = get_connection()
    try:
        # Search forward from current_index
        cur = conn.execute("""
            SELECT a.item_index
            FROM assignments a
            LEFT JOIN ratings r ON a.response_id = r.response_id
            WHERE a.annotator_id = ? AND a.item_index >= ? AND r.response_id IS NULL
            ORDER BY a.item_index ASC
            LIMIT 1;
        """, (annotator_id, current_index))
        row = cur.fetchone()
        if row:
            return row["item_index"]

        # Wrap around to beginning
        cur_wrap = conn.execute("""
            SELECT a.item_index
            FROM assignments a
            LEFT JOIN ratings r ON a.response_id = r.response_id
            WHERE a.annotator_id = ? AND r.response_id IS NULL
            ORDER BY a.item_index ASC
            LIMIT 1;
        """, (annotator_id,))
        row_wrap = cur_wrap.fetchone()
        if row_wrap:
            return row_wrap["item_index"]

        # All items completed
        return current_index
    finally:
        conn.close()

def save_rating(
    annotator_id: str,
    assignment_id: str,
    fluency: int,
    code_mixing_naturalness: int,
    hindi_grammar: int,
    prompt_adherence: int,
    spelling_consistency: int,
    overall: int,
    notes: Optional[str] = ""
) -> Tuple[bool, str, Dict[str, Any]]:
    scores = {
        "fluency": fluency,
        "code_mixing_naturalness": code_mixing_naturalness,
        "hindi_grammar": hindi_grammar,
        "prompt_adherence": prompt_adherence,
        "spelling_consistency": spelling_consistency,
        "overall": overall
    }
    for dim, score in scores.items():
        if not isinstance(score, int) or score < 1 or score > 5:
            return False, f"Invalid score for '{dim}': {score}. Must be an integer between 1 and 5.", {}

    conn = get_connection()
    try:
        with conn:
            cur_assign = conn.execute(
                "SELECT response_id, annotator_id, item_index FROM assignments WHERE assignment_id = ?;",
                (assignment_id,)
            )
            assign_row = cur_assign.fetchone()
            if not assign_row:
                return False, f"Assignment '{assignment_id}' not found.", {}
            
            if assign_row["annotator_id"] != annotator_id:
                return False, "Access Denied: You cannot submit ratings for another annotator's assignment.", {}
            
            resp_id = assign_row["response_id"]
            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

            cur_existing = conn.execute("SELECT * FROM ratings WHERE response_id = ?;", (resp_id,))
            existing = cur_existing.fetchone()

            if existing:
                old_scores = {
                    "fluency": existing["fluency"],
                    "code_mixing_naturalness": existing["code_mixing_naturalness"],
                    "hindi_grammar": existing["hindi_grammar"],
                    "prompt_adherence": existing["prompt_adherence"],
                    "spelling_consistency": existing["spelling_consistency"],
                    "overall": existing["overall"],
                    "notes": existing["notes"]
                }
                action = "UPDATE"
                conn.execute("""
                    UPDATE ratings SET
                        fluency = ?,
                        code_mixing_naturalness = ?,
                        hindi_grammar = ?,
                        prompt_adherence = ?,
                        spelling_consistency = ?,
                        overall = ?,
                        notes = ?,
                        updated_at = ?,
                        assignment_status = 'updated'
                    WHERE response_id = ?;
                """, (
                    fluency, code_mixing_naturalness, hindi_grammar,
                    prompt_adherence, spelling_consistency, overall,
                    notes, now_iso, resp_id
                ))

                conn.execute("""
                    INSERT INTO ratings_audit_trail (response_id, annotator_id, action, old_values, new_values, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?);
                """, (
                    resp_id, annotator_id, action,
                    json.dumps(old_scores), json.dumps(scores), now_iso
                ))
                status_msg = "Rating updated successfully."
            else:
                action = "INSERT"
                conn.execute("""
                    INSERT INTO ratings (
                        response_id, assignment_id, annotator_id,
                        fluency, code_mixing_naturalness, hindi_grammar,
                        prompt_adherence, spelling_consistency, overall,
                        notes, submitted_at, updated_at, assignment_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'completed');
                """, (
                    resp_id, assignment_id, annotator_id,
                    fluency, code_mixing_naturalness, hindi_grammar,
                    prompt_adherence, spelling_consistency, overall,
                    notes, now_iso, now_iso
                ))

                conn.execute("""
                    INSERT INTO ratings_audit_trail (response_id, annotator_id, action, old_values, new_values, timestamp)
                    VALUES (?, ?, ?, NULL, ?, ?);
                """, (
                    resp_id, annotator_id, action, json.dumps(scores), now_iso
                ))
                status_msg = "Rating saved successfully."

        progress = get_annotator_progress(annotator_id)
        return True, status_msg, progress
    except Exception as e:
        return False, f"Database error: {str(e)}", {}
    finally:
        conn.close()
