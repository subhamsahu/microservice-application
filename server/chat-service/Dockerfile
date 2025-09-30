# Production Dockerfile for Chat Service
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy Poetry configuration
COPY pyproject.toml poetry.lock ./

# Configure Poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --only=main --no-interaction --no-ansi

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash chatuser
RUN chown -R chatuser:chatuser /app
USER chatuser

# Expose port
EXPOSE 4004

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:4004/api/v1/chat/health || exit 1

# Run the application
CMD ["python", "server.py"]