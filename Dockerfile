# Dockerfile for Django API
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --upgrade pip && pip install uv

# Copy the pyproject.toml, setup.py and src directory
COPY pyproject.toml .
COPY setup.py .
COPY src/ ./src/

# Install Python dependencies using uv in system mode
RUN uv pip install --system --no-cache-dir -e .

# Copy the remaining application code
COPY . .

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "src.core.wsgi:application"]
