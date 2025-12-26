# Build stage
FROM python:3.10-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Download RTMDet model (optional - for self-contained image)
# RUN mkdir -p /build/checkpoints && \
#     wget -O /build/checkpoints/rtmdet_tiny.pth \
#     https://download.openmmlab.com/mmdetection/v3.0/rtmdet/rtmdet_tiny_8xb32-300e_coco/rtmdet_tiny_8xb32-300e_coco_20220902_112414-78e30dcc.pth

# Runtime stage
FROM python:3.10-slim

LABEL maintainer="your-email@example.com"
LABEL description="FESS Motion Detection System"
LABEL version="1.0.0"

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    curl \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user early
RUN useradd -m -u 1000 fess

# Copy Python packages from builder to a location accessible by fess
COPY --from=builder /root/.local /home/fess/.local
RUN chown -R fess:fess /home/fess/.local/

# Copy application code
COPY src/ ./src/
COPY known_faces/ ./known_faces/

# Create directories for configs and checkpoints
RUN mkdir -p ./configs ./checkpoints ./logs ./docker && \
    chown -R fess:fess /app

# Add local Python packages to PATH
ENV PATH=/home/fess/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUSERBASE=/home/fess/.local

# Copy entrypoint script
COPY docker/entrypoint.sh /app/docker/entrypoint.sh
RUN chmod +x /app/docker/entrypoint.sh && \
    chown fess:fess /app/docker/entrypoint.sh

USER fess

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose ports
EXPOSE 8000

# Entry point
ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["python", "-m", "src.main"]
