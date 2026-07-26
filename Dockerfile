# Multi-stage Dockerfile for Gaia
# Production-ready build with Poetry, CUDA support, and optimized image layers

# Stage 1: Base image with Python and system dependencies
FROM python:3.10-slim as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Stage 2: Builder stage for installing dependencies
FROM base as builder

WORKDIR /app

COPY pyproject.toml poetry.lock* README.md ./

# Install only production dependencies in virtual environment
RUN poetry install --only main --no-root --no-directory

# Copy source code and install project
COPY configs/ ./configs/
COPY datasets/ ./datasets/
COPY preprocessing/ ./preprocessing/
COPY feature_engineering/ ./feature_engineering/
COPY models/ ./models/
COPY training/ ./training/
COPY evaluation/ ./evaluation/
COPY visualization/ ./visualization/
COPY api/ ./api/
COPY scripts/ ./scripts/

RUN poetry install --only main

# Stage 3: Lightweight runtime stage
FROM python:3.10-slim as runtime

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*
    
# Create non-root user for security
RUN groupadd -r climate && useradd -r -g climate climate

# Copy virtual environment and source code from builder
COPY --from=builder --chown=climate:climate /app /app

USER climate

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["python", "-m", "uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
