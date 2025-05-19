FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY setup.py pyproject.toml README.md ./
COPY src ./src/

# Install dependencies
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir . && \
    # Install Git Repository Analyzer plugin dependencies
    pip install --no-cache-dir gitpython>=3.1.0 plotly>=5.10.0 pandas>=1.3.0 tabulate>=0.8.0

# Install git and tree commands
RUN apt-get update && apt-get install -y tree git && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user and switch to it
RUN addgroup --system nonroot && adduser --system --ingroup nonroot nonroot

# Set environment variables
ENV FLASK_APP=src
ENV FLASK_FILE_EXPLORER_BASE_DIR=/data
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
# Enable DEBUG logging
ENV PYTHONUNBUFFERED=1
ENV FLASK_DEBUG=1

# Create a data directory to mount user files
RUN mkdir -p /data

# Expose port 5000
EXPOSE 5000

# Give ownership of the data directory to the nonroot user
RUN chown -R nonroot:nonroot /data
USER nonroot

# Command to run the application using Python's module execution
CMD ["python", "-m", "src"]