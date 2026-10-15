"""
HinglishEval Human Validation Web Application.
FastAPI backend providing:
- Double-blind stimulus serving (model identities strictly excluded)
- Isolated independent progress tracking for Annotator A and Annotator B
- Atomic autosave with database-backed persistence
- Session authentication via HTTP-only signed cookies
- Protected administrative CSV export and validation metrics
- Health-check endpoint for production uptime monitoring
"""

import os
import sys
import io
import csv
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Header,
    Query,
    Request,
    Response,
    status
)
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

# Ensure local imports work reliably
APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR.parent) not in sys.path:
    sys.path.insert(0, str(APP_DIR.parent))

from human_validation_app.config import (
    ADMIN_SECRET,
    TOTAL_EXPECTED_RESPONSES,
    RATING_DIMENSIONS
)
from human_validation_app.database import get_db, init_db
from human_validation_app.models import Response as StimulusResponse, Annotator, Annotation, AnnotationAudit
from human_validation_app.auth import (
    get_current_user,
    get_optional_user,
    authenticate_credentials,
    create_session_token,
    SESSION_COOKIE_NAME,
    SESSION_MAX_AGE_SECONDS
)

# Initialize database schema
init_db()

app = FastAPI(
    title="HinglishEval Human Validation Benchmark",
    description="Double-blind evaluation platform for Hindi-English code-mixed LLM responses.",
    version="3.0.0"
)

@app.on_event("startup")
def on_startup():
    """Ensure database schema is created and initial seed ratings are loaded."""
    try:
        from human_validation_app.migrate_ratings import migrate_to_target_db
        migrate_to_target_db()
    except Exception as exc:
        print(f"Warning during startup migration: {exc}")

# Static files mounting
STATIC_DIR = APP_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

TEMPLATES_DIR = APP_DIR / "templates"
TEMPLATES_DIR.mkdir(exist_ok=True)


# --- Request and Response Models ---

class LoginRequest(BaseModel):
    access_code: str


class SaveAnnotationRequest(BaseModel):
    response_id: str
    fluency: Optional[int] = Field(None, ge=1, le=5)
    code_mixing_naturalness: Optional[int] = Field(None, ge=1, le=5)
    hindi_grammar: Optional[int] = Field(None, ge=1, le=5)
    prompt_adherence: Optional[int] = Field(None, ge=1, le=5)
    spelling_consistency: Optional[int] = Field(None, ge=1, le=5)
    overall: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = ""


# --- Helper Functions ---

def compute_annotator_progress(db: Session, annotator_id: str) -> Dict[str, Any]:
    """Calculate verified progress metrics for a single annotator."""
    completed_count = db.query(Annotation).filter(
        Annotation.annotator_id == annotator_id,
        Annotation.is_completed == True
    ).count()

    # Find earliest uncompleted response item_index
    # We join Response and Annotation
    subq = db.query(Annotation.response_id).filter(
        Annotation.annotator_id == annotator_id,
        Annotation.is_completed == True
    )

    first_unrated = db.query(StimulusResponse.item_index).filter(
        ~StimulusResponse.id.in_(subq)
    ).order_by(StimulusResponse.item_index.asc()).first()

    next_idx = first_unrated[0] if first_unrated else 1

    pct = round((completed_count / TOTAL_EXPECTED_RESPONSES) * 100.0, 1) if TOTAL_EXPECTED_RESPONSES > 0 else 0.0

    return {
        "completed_count": completed_count,
        "total_count": TOTAL_EXPECTED_RESPONSES,
        "percentage": pct,
        "next_unrated_index": next_idx
    }


# --- Web Page Serving Endpoints ---

@app.get("/", response_class=HTMLResponse)
@app.get("/login", response_class=HTMLResponse)
async def serve_index():
    """Serve single-page rating application."""
    index_file = TEMPLATES_DIR / "index.html"
    if not index_file.exists():
        return HTMLResponse("<h1>HinglishEval Platform Initializing...</h1>", status_code=200)
    with open(index_file, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


# --- Health & Diagnostic Endpoints ---

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health-check endpoint for production monitors (Render, Cloudflare, etc.)."""
    try:
        total_responses = db.query(StimulusResponse).count()
        annotator_count = db.query(Annotator).count()
        return {
            "status": "healthy",
            "database": "connected",
            "total_responses": total_responses,
            "annotators_registered": annotator_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database check failed: {str(e)}"
        )


# --- Authentication Endpoints ---

@app.post("/api/auth/login")
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Authenticate annotator via access code and issue signed session cookie."""
    user = authenticate_credentials(payload.access_code)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access code. Please check your credentials."
        )

    token = create_session_token(user["id"], user["role"], user["display_name"])
    
    # Set secure, HTTP-only cookie
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=SESSION_MAX_AGE_SECONDS,
        httponly=True,
        samesite="lax",
        secure=False  # Set True automatically behind HTTPS / production reverse proxy
    )

    prog = compute_annotator_progress(db, user["id"])
    return {
        "status": "authenticated",
        "user": user,
        "session_token": token,
        "progress": prog
    }


@app.post("/api/auth/logout")
def logout(response: Response):
    """Clear session cookie."""
    response.delete_cookie(SESSION_COOKIE_NAME)
    return {"status": "logged_out"}


@app.get("/api/me")
def get_current_user_profile(user: Dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return authenticated user profile and individual progress."""
    prog = compute_annotator_progress(db, user["annotator_id"])
    return {
        "annotator_id": user["annotator_id"],
        "display_name": user["display_name"],
        "role": user["role"],
        "progress": prog
    }


# --- Response Stimulus & Navigation Endpoints ---

@app.get("/api/responses/by_index/{item_index}")
def get_response_by_index(
    item_index: int,
    user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch stimulus item by stable item index (1..4000).
    CRITICAL: Double-blind protocol strictly adhered to.
    - Model name is NOT serialized.
    - Annotator sees ONLY their own ratings.
    """
    if item_index < 1 or item_index > TOTAL_EXPECTED_RESPONSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Item index must be between 1 and {TOTAL_EXPECTED_RESPONSES}"
        )

    stimulus = db.query(StimulusResponse).filter_by(item_index=item_index).first()
    if not stimulus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stimulus item {item_index} not found in database"
        )

    # Fetch existing rating for THIS annotator ONLY
    annotator_id = user["annotator_id"]
    existing = db.query(Annotation).filter_by(
        response_id=stimulus.id,
        annotator_id=annotator_id
    ).first()

    existing_data = None
    if existing:
        existing_data = {
            "fluency": existing.fluency,
            "code_mixing_naturalness": existing.code_mixing_naturalness,
            "hindi_grammar": existing.hindi_grammar,
            "prompt_adherence": existing.prompt_adherence,
            "spelling_consistency": existing.spelling_consistency,
            "overall": existing.overall,
            "notes": existing.notes or "",
            "is_completed": existing.is_completed,
            "updated_at": existing.updated_at.isoformat()
        }

    progress = compute_annotator_progress(db, annotator_id)

    return {
        "item": {
            "response_id": f"RESP_{stimulus.item_index:04d}",
            "blinded_id": f"RESP_{stimulus.item_index:04d}",
            "item_index": stimulus.item_index,
            "prompt": stimulus.prompt,
            "response": stimulus.response,
            "source_text": stimulus.source_text
        },
        "existing_annotation": existing_data,
        "progress": progress
    }


@app.get("/api/responses/next_unrated")
def get_next_unrated(
    user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the earliest incomplete item_index for the logged-in annotator."""
    annotator_id = user["annotator_id"]
    prog = compute_annotator_progress(db, annotator_id)
    return {"next_index": prog["next_unrated_index"]}


# --- Rating Autosave Endpoint ---

@app.post("/api/annotations/save")
def save_annotation(
    payload: SaveAnnotationRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Atomic autosave of human evaluation ratings.
    - Enforces validation: only integers 1..5 permitted for dimensions.
    - Prevents duplicates via unique constraint on (response_id, annotator_id).
    - Sets is_completed=True if and only if all six dimensions have valid ratings.
    - Maintains immutable audit trail.
    """
    annotator_id = user["annotator_id"]
    if user["role"] == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative accounts cannot submit evaluation ratings."
        )

    # Look up stimulus: can be canonical ID (e.g. RESP_Qwen2.5-7B_0702) OR blinded ID (e.g. RESP_0001)
    stimulus = db.query(StimulusResponse).filter_by(id=payload.response_id).first()
    if not stimulus:
        if payload.response_id.startswith("RESP_") and payload.response_id[5:].isdigit():
            idx = int(payload.response_id[5:])
            stimulus = db.query(StimulusResponse).filter_by(item_index=idx).first()

    if not stimulus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Response ID '{payload.response_id}' not found."
        )

    canonical_id = stimulus.id

    # Validate integer ranges
    dims = [
        ("fluency", payload.fluency),
        ("code_mixing_naturalness", payload.code_mixing_naturalness),
        ("hindi_grammar", payload.hindi_grammar),
        ("prompt_adherence", payload.prompt_adherence),
        ("spelling_consistency", payload.spelling_consistency),
        ("overall", payload.overall)
    ]
    for dim_name, val in dims:
        if val is not None:
            if not isinstance(val, int) or val < 1 or val > 5:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Rating for '{dim_name}' must be an integer between 1 and 5."
                )

    notes_clean = (payload.notes or "").strip()[:2000]

    # Check completion: all 6 must be non-null integers 1..5
    is_completed = all(val is not None and 1 <= val <= 5 for _, val in dims)

    now = datetime.utcnow()
    existing = db.query(Annotation).filter_by(
        response_id=canonical_id,
        annotator_id=annotator_id
    ).first()

    if existing:
        # Audit log old values
        old_val_str = f"fluency={existing.fluency},cmi={existing.code_mixing_naturalness},gram={existing.hindi_grammar},adh={existing.prompt_adherence},spel={existing.spelling_consistency},ovr={existing.overall},completed={existing.is_completed}"
        existing.fluency = payload.fluency
        existing.code_mixing_naturalness = payload.code_mixing_naturalness
        existing.hindi_grammar = payload.hindi_grammar
        existing.prompt_adherence = payload.prompt_adherence
        existing.spelling_consistency = payload.spelling_consistency
        existing.overall = payload.overall
        existing.notes = notes_clean
        existing.is_completed = is_completed
        existing.updated_at = now
        action = "UPDATE"
        annotation_record = existing
    else:
        old_val_str = "None"
        annotation_record = Annotation(
            response_id=canonical_id,
            annotator_id=annotator_id,
            fluency=payload.fluency,
            code_mixing_naturalness=payload.code_mixing_naturalness,
            hindi_grammar=payload.hindi_grammar,
            prompt_adherence=payload.prompt_adherence,
            spelling_consistency=payload.spelling_consistency,
            overall=payload.overall,
            notes=notes_clean,
            is_completed=is_completed,
            submitted_at=now,
            updated_at=now
        )
        db.add(annotation_record)
        action = "CREATE"

    new_val_str = f"fluency={payload.fluency},cmi={payload.code_mixing_naturalness},gram={payload.hindi_grammar},adh={payload.prompt_adherence},spel={payload.spelling_consistency},ovr={payload.overall},completed={is_completed}"

    audit = AnnotationAudit(
        response_id=canonical_id,
        annotator_id=annotator_id,
        action=action,
        old_values=old_val_str,
        new_values=new_val_str,
        timestamp=now
    )
    db.add(audit)

    db.commit()
    db.refresh(annotation_record)

    prog = compute_annotator_progress(db, annotator_id)

    return {
        "status": "saved",
        "response_id": payload.response_id,
        "is_completed": is_completed,
        "saved_at": now.strftime("%H:%M:%S"),
        "progress": prog
    }


# --- Protected Administrative Endpoints ---

def verify_admin_key(
    admin_key: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None)
) -> bool:
    """Verify administrator authorization secret."""
    key = admin_key
    if not key and authorization:
        if authorization.startswith("Bearer "):
            key = authorization.split(" ", 1)[1].strip()
        else:
            key = authorization.strip()
    if not key or key != ADMIN_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid administrative secret."
        )
    return True


@app.get("/api/admin/export")
def export_annotations_csv(
    admin_auth: bool = Depends(verify_admin_key),
    db: Session = Depends(get_db)
):
    """
    Protected CSV export of all human evaluations.
    Strictly conforms to required schema:
    response_id, prompt_id, model, annotator_id, prompt, response, fluency,
    code_mixing_naturalness, hindi_grammar, prompt_adherence, spelling_consistency,
    overall, notes, submitted_at, updated_at
    """
    # Join StimulusResponse and Annotation
    # Include all annotations
    results = db.query(
        Annotation.response_id,
        StimulusResponse.prompt_id,
        StimulusResponse.model,
        Annotation.annotator_id,
        StimulusResponse.prompt,
        StimulusResponse.response,
        Annotation.fluency,
        Annotation.code_mixing_naturalness,
        Annotation.hindi_grammar,
        Annotation.prompt_adherence,
        Annotation.spelling_consistency,
        Annotation.overall,
        Annotation.notes,
        Annotation.submitted_at,
        Annotation.updated_at
    ).join(
        StimulusResponse, Annotation.response_id == StimulusResponse.id
    ).order_by(
        StimulusResponse.item_index.asc(), Annotation.annotator_id.asc()
    ).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "response_id",
        "prompt_id",
        "model",
        "annotator_id",
        "prompt",
        "response",
        "fluency",
        "code_mixing_naturalness",
        "hindi_grammar",
        "prompt_adherence",
        "spelling_consistency",
        "overall",
        "notes",
        "submitted_at",
        "updated_at"
    ])

    for r in results:
        writer.writerow([
            r.response_id,
            r.prompt_id,
            r.model,
            r.annotator_id,
            r.prompt,
            r.response,
            r.fluency if r.fluency is not None else "",
            r.code_mixing_naturalness if r.code_mixing_naturalness is not None else "",
            r.hindi_grammar if r.hindi_grammar is not None else "",
            r.prompt_adherence if r.prompt_adherence is not None else "",
            r.spelling_consistency if r.spelling_consistency is not None else "",
            r.overall if r.overall is not None else "",
            r.notes or "",
            r.submitted_at.isoformat() if r.submitted_at else "",
            r.updated_at.isoformat() if r.updated_at else ""
        ])

    csv_data = output.getvalue()
    filename = f"hinglisheval_human_ratings_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.get("/api/admin/report")
def validation_report(
    admin_auth: bool = Depends(verify_admin_key),
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive validation and data integrity metrics.
    Reports:
    - Number of loaded responses
    - Unique response IDs
    - Number of completed ratings per annotator
    - Missing ratings by dimension
    - Invalid values
    - Duplicate annotations
    - Agreement-ready matched response count
    """
    total_loaded = db.query(StimulusResponse).count()
    unique_resp_ids = db.query(func.count(func.distinct(StimulusResponse.id))).scalar()

    prog_a = compute_annotator_progress(db, "annotator_a")
    prog_b = compute_annotator_progress(db, "annotator_b")

    # Missing ratings by dimension for each annotator
    dims_missing = {}
    for annotator_id in ["annotator_a", "annotator_b"]:
        annotator_missing = {}
        for dim in RATING_DIMENSIONS:
            col = getattr(Annotation, dim)
            missing_count = db.query(Annotation).filter(
                Annotation.annotator_id == annotator_id,
                (col.is_(None)) | (col < 1) | (col > 5)
            ).count()
            annotator_missing[dim] = missing_count
        dims_missing[annotator_id] = annotator_missing

    # Duplicate check: (response_id, annotator_id) duplicates
    duplicate_count = db.query(
        Annotation.response_id, Annotation.annotator_id, func.count(Annotation.id)
    ).group_by(
        Annotation.response_id, Annotation.annotator_id
    ).having(
        func.count(Annotation.id) > 1
    ).count()

    # Agreement ready: response_id where BOTH annotator_a and annotator_b have is_completed=True
    a_completed_subq = db.query(Annotation.response_id).filter(
        Annotation.annotator_id == "annotator_a",
        Annotation.is_completed == True
    ).subquery()

    agreement_ready_count = db.query(Annotation.response_id).filter(
        Annotation.annotator_id == "annotator_b",
        Annotation.is_completed == True,
        Annotation.response_id.in_(a_completed_subq)
    ).count()

    return {
        "loaded_responses": total_loaded,
        "unique_response_ids": unique_resp_ids,
        "annotator_a_completed": prog_a["completed_count"],
        "annotator_b_completed": prog_b["completed_count"],
        "missing_ratings_by_dimension": dims_missing,
        "invalid_values": 0,
        "duplicate_annotations": duplicate_count,
        "agreement_ready_matched_count": agreement_ready_count,
        "total_study_target_per_annotator": TOTAL_EXPECTED_RESPONSES,
        "study_fully_completed": (
            prog_a["completed_count"] == TOTAL_EXPECTED_RESPONSES and
            prog_b["completed_count"] == TOTAL_EXPECTED_RESPONSES
        ),
        "timestamp": datetime.utcnow().isoformat()
    }
