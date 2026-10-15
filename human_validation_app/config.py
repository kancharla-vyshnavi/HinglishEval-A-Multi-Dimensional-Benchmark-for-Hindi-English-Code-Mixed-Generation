"""
Configuration settings for HinglishEval Human Validation Web Application.
Supports local SQLite development and production PostgreSQL deployment (e.g. Render).
"""

import os
from pathlib import Path

# Base paths
APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{APP_DIR}/ratings_4000.db")
# Render / Heroku compatibility: convert postgres:// to postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Security and Credentials
# Default keys provided for local development and initial deployment.
# In production, these should be overridden via environment variables.
ANNOTATOR_A_KEY = os.getenv("ANNOTATOR_A_KEY", "eval_a_lead_2026")
ANNOTATOR_B_KEY = os.getenv("ANNOTATOR_B_KEY", "eval_b_partner_2026")
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "admin_hinglish_master_2026")
SECRET_KEY = os.getenv("SECRET_KEY", "hinglisheval_production_secret_key_salt_2026")

# Data file paths
DEFAULT_GENERATIONS_CSV = PROJECT_ROOT / "outputs" / "controlled_1000" / "benchmark_generations_.csv"
DEFAULT_BENCHMARK_CSV = PROJECT_ROOT / "data" / "benchmarks" / "hinglish_bench_.csv"

# Study parameters
TOTAL_EXPECTED_RESPONSES = 4000
EXPECTED_MODELS = ["HingGPT", "Phi-3.5-mini", "Qwen2.5-3B", "Qwen2.5-7B"]
RATING_DIMENSIONS = [
    "fluency",
    "code_mixing_naturalness",
    "hindi_grammar",
    "prompt_adherence",
    "spelling_consistency",
    "overall"
]
