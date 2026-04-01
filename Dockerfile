# ---- Stage 1: Build / dependency install ----
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: Production image ----
FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Remove files not needed at runtime
RUN rm -f Dockerfile .dockerignore .env.example .gitignore \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Gunicorn production server:
#   --workers 4        : handle concurrent requests
#   --bind 0.0.0.0:8000: listen on all interfaces
#   --access-logfile - : stream access logs to stdout (for Azure Monitor / container logs)
#   --timeout 120      : allow up to 120s per request
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--timeout", "120", "app:app"]