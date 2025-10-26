ARG BUILD_FROM=ghcr.io/home-assistant/base-python:3.11-alpine3.18
FROM $BUILD_FROM

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    nginx \
    curl \
    jq \
    tzdata \
    && rm -rf /var/cache/apk/*

# Copy Python requirements and install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the application
COPY planty/ ./planty/
COPY web/ ./web/
COPY nginx.conf /etc/nginx/nginx.conf
COPY run.sh .

# Create necessary directories
RUN mkdir -p /data/planty \
    && mkdir -p /share/planty/images \
    && mkdir -p /var/log/nginx \
    && chmod +x run.sh

# Expose port
EXPOSE 8099

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8099/health || exit 1

# Set the entrypoint
ENTRYPOINT ["./run.sh"]
