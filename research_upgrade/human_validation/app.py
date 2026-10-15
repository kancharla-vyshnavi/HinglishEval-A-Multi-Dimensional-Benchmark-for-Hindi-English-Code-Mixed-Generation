"""
app.py
Production-grade FastAPI server for HinglishEval human evaluation.
Serves the blinded rating interface, enforces access control, and persists ratings to SQLite.
"""

import os
import sys
import json
import sqlite3
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Header, Query, Request, Response, status
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Ensure local imports work cleanly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import db

app = FastAPI(
    title="HinglishEval Human Evaluation Platform",
    description="Double-blind bilingual human rating platform for Hindi-English code-mixed LLM generation.",
    version="2.0.0"
)

# Ensure database and tables exist
db.init_db()

# Serve static directory
STATIC_DIR = os.path.join(CURRENT_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Request Models
class RatingSubmission(BaseModel):
    assignment_id: str
    fluency: int = Field(..., ge=1, le=5)
    code_mixing_naturalness: int = Field(..., ge=1, le=5)
    hindi_grammar: int = Field(..., ge=1, le=5)
    prompt_adherence: int = Field(..., ge=1, le=5)
    spelling_consistency: int = Field(..., ge=1, le=5)
    overall: int = Field(..., ge=1, le=5)
    notes: Optional[str] = ""

def verify_token(token: Optional[str]) -> Dict[str, str]:
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required. Please provide a valid access token.")
    clean_tok = token.strip()
    if clean_tok == "eval_b_partner_2026":
        raise HTTPException(status_code=403, detail="Partner (Annotator B) access is currently disabled. Only Annotator A is active.")
    info = db.authenticate_token(clean_tok)
    if not info:
        raise HTTPException(status_code=403, detail="Invalid access token. Unauthorized access.")
    return info

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(CURRENT_DIR, "templates", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>HinglishEval Interface Initializing...</h1>", status_code=200)

@app.get("/api/session")
async def get_session(token: str = Query(...)):
    user = verify_token(token)
    annotator_id = user["annotator_id"]
    if user["role"] == "admin":
        prog_a = db.get_annotator_progress("annotator_a")
        prog_b = db.get_annotator_progress("annotator_b")
        return {
            "annotator_id": "admin",
            "name": user["name"],
            "role": "admin",
            "progress_a": prog_a,
            "progress_b": prog_b
        }
    progress = db.get_annotator_progress(annotator_id)
    return {
        "annotator_id": annotator_id,
        "name": user["name"],
        "role": user["role"],
        "progress": progress
    }

@app.get("/api/item")
async def get_item(item_index: int = Query(1, ge=1, le=500), token: str = Query(...)):
    user = verify_token(token)
    annotator_id = user["annotator_id"]
    if user["role"] == "admin":
        annotator_id = "annotator_a"

    item = db.get_assignment_item(annotator_id, item_index)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_index} not found for this annotator.")
    
    progress = db.get_annotator_progress(annotator_id)
    return {
        "item": item,
        "progress": progress
    }

@app.get("/api/next_unanswered")
async def get_next_unanswered(current_index: int = Query(1, ge=1, le=500), token: str = Query(...)):
    user = verify_token(token)
    annotator_id = user["annotator_id"]
    if user["role"] == "admin":
        annotator_id = "annotator_a"
    next_idx = db.get_next_unanswered_index(annotator_id, current_index)
    return {"next_index": next_idx}

@app.post("/api/rate")
async def submit_rating(payload: RatingSubmission, token: str = Query(...)):
    user = verify_token(token)
    annotator_id = user["annotator_id"]
    if user["role"] == "admin":
        # Admin cannot submit ratings to preserve human data integrity
        raise HTTPException(status_code=403, detail="Admin accounts cannot submit ratings. Please log in as an assigned annotator.")

    success, msg, progress = db.save_rating(
        annotator_id=annotator_id,
        assignment_id=payload.assignment_id,
        fluency=payload.fluency,
        code_mixing_naturalness=payload.code_mixing_naturalness,
        hindi_grammar=payload.hindi_grammar,
        prompt_adherence=payload.prompt_adherence,
        spelling_consistency=payload.spelling_consistency,
        overall=payload.overall,
        notes=payload.notes
    )
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    
    return {
        "success": True,
        "message": msg,
        "progress": progress
    }

@app.get("/api/admin/overview")
async def get_admin_overview(token: str = Query(...)):
    user = verify_token(token)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin privilege required.")
    
    conn = db.get_connection()
    try:
        prog_a = db.get_annotator_progress("annotator_a")
        prog_b = db.get_annotator_progress("annotator_b")

        # Recent audit logs
        cur_logs = conn.execute("""
            SELECT audit_id, response_id, annotator_id, action, timestamp
            FROM ratings_audit_trail
            ORDER BY audit_id DESC LIMIT 15;
        """)
        recent_logs = [dict(r) for r in cur_logs.fetchall()]

        # Model completion breakdown
        cur_models = conn.execute("""
            SELECT a.model, a.annotator_id, COUNT(r.response_id) as completed_count
            FROM assignments a
            LEFT JOIN ratings r ON a.response_id = r.response_id
            GROUP BY a.model, a.annotator_id;
        """)
        model_stats = [dict(r) for r in cur_models.fetchall()]

        return {
            "progress_a": prog_a,
            "progress_b": prog_b,
            "recent_audit_trail": recent_logs,
            "model_completion_breakdown": model_stats
        }
    finally:
        conn.close()

@app.post("/api/export")
async def run_export_pipeline(token: str = Query(...)):
    user = verify_token(token)
    # Both lead annotator and admin can trigger export
    if user["annotator_id"] not in ["annotator_a", "admin"]:
        raise HTTPException(status_code=403, detail="Only Lead Annotator A or Admin can trigger data export.")
    
    # Import and run combine_and_validate_ratings
    import combine_and_validate_ratings
    report = combine_and_validate_ratings.combine_and_validate()
    return {
        "success": True,
        "message": "Export completed successfully.",
        "summary": report
    }

@app.get("/api/download/{filename}")
async def download_file(filename: str, token: str = Query(...)):
    verify_token(token)
    allowed_files = [
        "combined_human_ratings_1000.csv",
        "annotator_A_ratings.csv",
        "annotator_B_ratings.csv",
        "human_validation_report.md",
        "human_evaluation_validation_report.md",
        "assignment_manifest.csv"
    ]
    if filename not in allowed_files:
        raise HTTPException(status_code=400, detail="Invalid file download request.")
    
    file_path = os.path.join(CURRENT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File has not been generated yet. Please run export first.")
    
    return FileResponse(path=file_path, filename=filename, media_type="text/csv" if filename.endswith(".csv") else "text/markdown")
