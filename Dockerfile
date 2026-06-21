# ── Build stage ────────────────────────────────────────────────────────────────
FROM python:3.12-slim

# System deps for psycopg (libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port Render will use
EXPOSE 8000

# Start with gunicorn — Render sets PORT env automatically
CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
