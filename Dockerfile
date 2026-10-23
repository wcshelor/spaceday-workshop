# syntax=docker/dockerfile:1
# Frontend builder — reproducible from source
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
# Build frontend (outputs to frontend/dist)
RUN npm run build

# Backend runtime
FROM python:3.11-slim
WORKDIR /app

# Install backend deps from authoritative pinned declarations (pyproject.toml)
# Exclude optional live-encoder dependencies (onnxruntime etc.) for this deployment
COPY backend/pyproject.toml backend/pyproject.toml
# Minimal setuptools requires pyproject and package dir to resolve install
COPY backend/app backend/app
RUN pip install --no-cache-dir ./backend

# Copy config, data, artifacts, content (artifacts include collaborative + scoring + prepared language)
COPY config config
COPY data/workshop data/workshop
COPY artifacts artifacts
COPY content content

# Copy built frontend from builder
COPY --from=frontend-builder /app/frontend/dist frontend/dist

ENV PYTHONPATH=/app
ENV SPACEDAY_DATA_DIR=/app/data/workshop
ENV SPACEDAY_SCORING_ARTIFACT=/app/artifacts/scoring-v1
ENV SPACEDAY_LANGUAGE_ARTIFACT=/app/artifacts/language-v1
ENV SPACEDAY_LANGUAGE_MODE=disabled
# Render provides PORT; default 8000
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
