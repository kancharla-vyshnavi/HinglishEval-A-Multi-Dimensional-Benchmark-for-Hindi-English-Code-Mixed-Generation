# Production Dockerfile for HinglishEval Human Validation Platform
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications
COPY human_validation_app/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application and dataset files
COPY outputs/controlled_1000 outputs/controlled_1000
COPY data/benchmarks data/benchmarks
COPY human_validation_app human_validation_app

# Run idempotent migration to prepare database schema and seed ratings
RUN python -m human_validation_app.migrate_ratings

# Expose port and configure health check
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Launch uvicorn web server
CMD ["sh", "-c", "uvicorn human_validation_app.app:app --host 0.0.0.0 --port ${PORT}"]
