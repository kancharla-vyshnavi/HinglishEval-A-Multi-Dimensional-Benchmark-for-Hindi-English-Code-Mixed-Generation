# HinglishEval Human Validation Platform — Progress Log

**Project:** HinglishEval — A Multi-Dimensional Benchmark for Hindi-English Code-Mixed Generation  
**App Path:** `c:\Users\vyshu\OneDrive\Desktop\HinglishLLM\human_validation_app`  
**Date:** 2026-10-14  

---

## Task Objectives
1. Inspect existing project, generation dataset, and prior human validation implementations.
2. Build a standalone, production-ready human validation web application under `human_validation_app/`.
3. Support two independent annotators (Annotator A and Annotator B) evaluating the same 4,000 generated responses (8,000 records total).
4. Enforce strict double-blind evaluation: model names hidden from annotators, zero cross-rater visibility.
5. Provide 6-dimension evaluation (1–5 integer Likert scale) with full rubrics and optional notes.
6. Implement server-side persistence, atomic autosave, and resume functionality.
7. Support PostgreSQL for production deployment (Render/cloud) and SQLite for local development.
8. Implement protected admin CSV export endpoint and statistical inter-annotator agreement analysis (Krippendorff's alpha, QWK).
9. Create automated test suite, deployment configuration (`render.yaml`, `Dockerfile`, `Procfile`), and live testing.

---

## Log of Actions

### Action 1 — Initial Inspection & Verification
- Inspected repository structure and git status.
- Located canonical 4,000-response generation file at `outputs/controlled_1000/benchmark_generations_.csv`.
  - Exactly 4,000 rows across 4 models (HingGPT: 1,000, Phi-3.5-mini: 1,000, Qwen2.5-3B: 1,000, Qwen2.5-7B: 1,000).
  - Verified 0 nulls, 0 empty strings.
- Located prompt benchmark at `data/benchmarks/hinglish_bench_.csv` (1,000 items: `prompt_id`, `row_index`, `prompt`, `source_text`).
- Verified 1:1 prompt correspondence: each model generated responses for all 1,000 benchmark prompts in exact identical order.
- Inspected existing rubric in `research_upgrade/human_validation/HUMAN_EVALUATION_OFFLINE_GUIDE.md` for reuse.
- Initialized `human_validation_app/` directory and progress log.

### Action 2 — Database Architecture & Models
- Built modular database layer in `database.py` and `models.py` using SQLAlchemy 2.0.
- Implemented dual backend support:
  - Production: Managed PostgreSQL via `DATABASE_URL` with connection pooling (`pool_pre_ping=True`, `pool_size=10`).
  - Development / Local: SQLite with WAL mode, foreign keys enabled, and timeout safeguards.
- Defined `Response`, `Annotator`, `Annotation`, and `AnnotationAudit` models.
- Enforced unique database constraint `(response_id, annotator_id)` on the `annotations` table to guarantee zero duplicate ratings.

### Action 3 — Data Ingestion & Deterministic Response IDs
- Developed `import_4000.py` for idempotent loading of all 4,000 responses.
- Generated clean, blinded response identifiers: `RESP_0001` through `RESP_4000`.
- Interleaved prompts across all 4 models in a deterministic, stable sequence so both annotators see items in the exact same order (items 1..4000).
- Model identities (`model`) are stored securely in the database for research export, but strictly stripped from all annotator-facing APIs.
- Verified idempotent re-import: returns verified status without duplicating or modifying existing annotations.

### Action 4 — Authentication, Authorization & Isolation
- Developed `auth.py` implementing PBKDF2-HMAC-SHA256 password hashing.
- Issued cryptographically signed, timestamped session tokens using `itsdangerous.URLSafeTimedSerializer`.
- Supported both HTTP-only session cookies (for seamless mobile web sessions) and `Authorization: Bearer <token>` headers (for programmatic API clients).
- Configured isolated accounts:
  - Annotator A: `eval_a_lead_2026`
  - Annotator B: `eval_b_partner_2026`
  - Admin: `admin_hinglish_master_2026`
- Strictly enforced annotator isolation: Annotator A and Annotator B cannot view or edit each other's ratings.

### Action 5 — Server API & Responsive Web Interface
- Developed FastAPI backend (`app.py`):
  - `GET /health`: Health-check endpoint reporting DB status, response count, and annotators.
  - `POST /api/auth/login` and `POST /api/auth/logout`: Session management.
  - `GET /api/me`: Profile and individual progress metrics.
  - `GET /api/responses/by_index/{item_index}`: Double-blind stimulus delivery.
  - `GET /api/responses/next_unrated`: Identifies earliest incomplete response for instant resumption.
  - `POST /api/annotations/save`: Atomic autosave, integer range validation (1..5), completion evaluation, and audit logging.
  - `GET /api/admin/export`: Protected CSV export with complete research schema.
  - `GET /api/admin/report`: Real-time validation metrics.
- Developed mobile-friendly, responsive Single Page Application:
  - `templates/index.html`: Clean, accessible layout with Stimulus panel, Scoring panel, Progress bar, and Rubric modal.
  - `static/style.css`: Vanilla CSS with modern typography (Inter), dark/light theme, high-contrast badges, and 48px tap targets.
  - `static/app.js`: Real-time autosave on radio click, debounced notes autosave, instant recovery on reconnection, and navigation guards.

### Action 6 — Export & Statistical Agreement Analysis
- Created `export_dataset.py` with CLI flags (`--output`, `--report`, `--report-file`).
- Created `analyze_agreement.py` calculating:
  - Klaus Krippendorff's Ordinal $\alpha$ with standard ordinal distance metric.
  - Quadratic Weighted Kappa (QWK) via scikit-learn.
  - Exact agreement (%) and $\pm 1$ agreement (%).
  - Non-parametric bootstrap 95% confidence intervals.
  - Strict empirical validity: Never fabricates annotations; honestly reports study completion status.

### Action 7 — Automated Testing
- Created comprehensive test suite `test_app.py` (10 test cases):
  1. `test_01_response_dataset_integrity`: Exactly 4,000 responses loaded, correct model coverage.
  2. `test_02_double_blind_stimulus_masking`: Model name strictly masked from annotator payload.
  3. `test_03_rating_validation_integers`: Rejection of out-of-range scores (0, 6).
  4. `test_04_completion_requires_all_six_dimensions`: Requires all 6 dimensions for `is_completed=True`.
  5. `test_05_duplicate_prevention_and_revision`: Revising rating updates row rather than duplicating.
  6. `test_06_annotator_isolation`: Annotator B sees None for Annotator A's ratings.
  7. `test_07_resume_next_unrated`: Accurately returns lowest incomplete index.
  8. `test_08_admin_export_authorization_and_schema`: Enforces admin secret and verifies CSV headers.
  9. `test_09_health_endpoint`: Reports healthy status and 4,000 response count.
  10. `test_10_agreement_analysis_implementation`: Verifies math calculations and graceful handling.
- Result: **10/10 tests passed (OK in 0.192s)**.

### Action 8 — Live HTTPS Deployment & Verification
- Configured Cloudflare tunnel and started local FastAPI server daemon.
- Generated verified public HTTPS URL: `https://brave-warranty-formula-crafts.trycloudflare.com`
- Executed end-to-end integration verification against the live HTTPS URL.
- Created deployment blueprint (`render.yaml`), `Dockerfile`, `Procfile`, and `README.md`.

### Action 9 — Preservation of Annotator A's 500 Ratings & Fresh Tunnel Restoration
- Backed up master database: `research_upgrade/human_validation/ratings_annotator_a_500_BACKUP_MASTER.db`.
- Rigorously audited Annotator A's ratings from `ratings.db`:
  - Exactly 500 completed response evaluations.
  - 100% valid scores across all six dimensions: `fluency`, `code_mixing_naturalness`, `hindi_grammar`, `prompt_adherence`, `spelling_consistency`, `overall` (scores 1..5, zero nulls).
  - Exact match of all 500 items to the canonical 4,000 benchmark dataset.
- Developed `sync_and_preserve.py` and updated `import_4000.py`:
  - Preserved original response IDs (`RESP_{model}_{row_index:04d}`).
  - Structured items 1..500 to map directly to Annotator A's evaluated items.
  - Structured items 501..4000 for the remaining 3,500 benchmark items.
  - Committed Annotator A's 500 completed ratings into `ratings_4000.db`.
  - Initialized Annotator B with exactly 0 completed ratings (all 4,000 pending).
- Solved DNS NXDOMAIN issue by relaunching tunnel with background pipe draining daemon:
  - Fresh verified public HTTPS URL: `https://press-acrylic-badly-meetings.trycloudflare.com`
- Executed live end-to-end HTTPS tests:
  - Health check 200 OK (`total_responses: 4000`, `database: connected`).
  - Annotator A login verified: `completed_count: 500`, `percentage: 12.5%`, `next_unrated_index: 501`.
  - Item 1 verified preserved with all 6 ratings.
  - Item 501 verified as next pending response for Annotator A.
  - Annotator B login verified: `completed_count: 0`, `percentage: 0.0%`, `next_unrated_index: 1`.
  - Item 1 for Annotator B verified as unrated (zero cross-rater score leakage).
  - Persistence verified: test save on item 4000 persisted across session restart and was cleanly purged.
  - Admin export endpoint verified over live HTTPS.
- 10/10 automated tests passed in `test_app.py`.
