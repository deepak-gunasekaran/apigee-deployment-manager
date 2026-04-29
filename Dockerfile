FROM python:3.11-slim

# Build arguments for metadata
ARG BUILD_DATE
ARG BUILD_VERSION
ARG COMMIT_SHA

# Set working directory
WORKDIR /app

# Install system dependencies and certificates
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Update pip and install certificates
RUN pip install --upgrade pip

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with trusted hosts
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Add build metadata as labels
LABEL org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.version="${BUILD_VERSION}" \
      org.opencontainers.image.revision="${COMMIT_SHA}" \
      org.opencontainers.image.title="Apigee Deployment Manager" \
      org.opencontainers.image.description="Enhanced web application for managing Apigee API proxy and shared flow deployments" \
      org.opencontainers.image.source="https://github.com/deepak-gunasekaran/apigee-deployment-manager" \
      maintainer="deepakdpk6"

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Run the application
CMD ["python", "app.py"]
