# Dockerfile for wary server
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY wary/ ./wary/

# Install Python dependencies
RUN pip install --no-cache-dir -e .[api,ui]
RUN pip install --no-cache-dir gunicorn psycopg2-binary

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV WARY_ENV=production

# Run server
CMD ["python", "-m", "wary.server"]
