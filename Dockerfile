# ============================================
# Stage 1: Builder
# ============================================
# 1. Start with the official Python image (Standard Docker Hub)
FROM python:3.12-slim-bookworm as builder

# 2. Copy the 'uv' binary from Astral's lightweight image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 3. Now use it exactly as before
WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT="/opt/venv"

# Copy lockfiles
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project --no-dev

# ============================================
# Stage 2: Runtime
# ============================================
FROM python:3.12-slim-bookworm

WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Add the venv to the path immediately
    PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -m -d /home/appuser appuser

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the Virtual Environment from builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Copy application code
COPY --chown=appuser:appuser . /app

# 🔴 OLD WAY (Don't do this anymore):
# COPY --chown=appuser:appuser ./entrypoint.sh /app/entrypoint.sh
# RUN chmod +x /app/entrypoint.sh

# ✅ NEW WAY (Move it to a system path):
COPY ./entrypoint.sh /usr/local/bin/entrypoint.sh

# Fix permissions AND fix Windows line endings (CRLF) in one go
RUN sed -i 's/\r$//g' /usr/local/bin/entrypoint.sh && chmod +x /usr/local/bin/entrypoint.sh

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Set the entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Default Command
# 🔴 CHANGED: core.asgi -> intelliresearchhub.asgi
CMD ["gunicorn", "intelliresearchhub.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]