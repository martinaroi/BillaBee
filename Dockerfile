# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=5000

# Copy pyproject.toml for dependency installation
COPY pyproject.toml .

# Install Python dependencies using pip with pyproject.toml
RUN pip install --no-cache-dir .

# Copy the application code
COPY app/ ./app/

# Create a non-root user
RUN useradd -m -u 1000 billabee && \
    chown -R billabee:billabee /app

# Switch to non-root user
USER billabee

# Expose the Flask port (Coolify will handle port mapping)
EXPOSE 5000

# Set the working directory to app folder
WORKDIR /app/app

# Run Flask with production server (gunicorn)
CMD ["python", "app.py"]
