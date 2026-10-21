# ========================================================================
# NEXUS GAMING ARENA - PRODUCTION CONTAINER DOCKERFILE
# Optimized for Google Cloud Run, AWS ECS, and Docker deployments
# ========================================================================

FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    APP_HOME=/app

WORKDIR $APP_HOME

# Install system dependencies (build-essential, curl, libffi)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python production dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create a secure, non-root system user
RUN groupadd -r nexusgroup && useradd -r -g nexusgroup -d $APP_HOME -s /sbin/nologin nexususer

# Copy application directories and files
COPY app/ ./app/
COPY templates/ ./templates/
COPY static/ ./static/
COPY nexus_gaming_arena.html ./
COPY data/ ./data/

# Ensure directories have proper permissions
RUN chown -R nexususer:nexusgroup $APP_HOME

# Switch to unprivileged non-root user for security
USER nexususer

# Expose internal port
EXPOSE 8080

# Healthcheck for Cloud Run / Docker container monitoring
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/api/health', timeout=4)" || exit 1

# Execute production uvicorn ASGI server
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 2 --proxy-headers --forwarded-allow-ips='*'"]
