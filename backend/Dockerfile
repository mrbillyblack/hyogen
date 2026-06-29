# Build context is the hyogen project root (see docker-compose.yml) so that we
# can install the vendored ytmusicapi fork alongside the backend.
FROM python:3.12-slim

WORKDIR /app

# Install backend dependencies first (layer caching).
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install the vendored ytmusicapi fork from source. ytmusicapi versions itself
# via setuptools_scm; pin a fallback so the build doesn't depend on git history.
COPY ytmusicapi /opt/ytmusicapi
RUN SETUPTOOLS_SCM_PRETEND_VERSION=0.0.0+hyogen \
    pip install --no-cache-dir /opt/ytmusicapi

# Copy the application code.
COPY backend/app ./app

EXPOSE 8000

# Cloud Run injects $PORT (8080); default to 8000 for local/compose use.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
