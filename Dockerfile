FROM python:3.11-slim

# Avoid interactive tzdata etc., faster pip, no .pyc files
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MPLBACKEND=Agg

# psycopg2-binary ships wheels, but build-essential is occasionally needed for other deps
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first to leverage Docker layer cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application source
COPY src/ ./src/

# Run from the backend directory so the existing relative imports
# (e.g. `from connectors.reddit_api import ...`) keep working.
WORKDIR /app/src/backend

# Default command: run the analysis pipeline once.
# Configure via env vars SEARCH_QUERY and SEARCH_LIMIT (see README / docker-compose.yml).
CMD ["python", "-u", "main.py"]
