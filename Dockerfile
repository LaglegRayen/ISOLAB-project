# ISOLAB Agri Support - Dockerfile
# Multi-stage build for production-ready Flask application

# Use Python 3.9 slim image as base
FROM python:3.9-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Debug: Check if Firebase config file exists
RUN echo "🔍 DEBUG: Checking if Firebase config file exists..." && \
    ls -la config/ && \
    if [ -f "config/isolab-support-firebase-adminsdk-fbsvc-7a36653eaf.json" ]; then \
        echo "✅ DEBUG: Firebase config file found in Docker image"; \
    else \
        echo "❌ DEBUG: Firebase config file NOT found in Docker image"; \
        ls -la .; \
    fi

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "app:app"]
