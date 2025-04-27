FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY setup.py pyproject.toml README.md ./
COPY src ./src/

# Install the package
RUN pip install --no-cache-dir -e .

# Set environment variables
ENV FLASK_APP=src
ENV FLASK_FILE_EXPLORER_BASE_DIR=/data
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Create a data directory to mount user files
RUN mkdir -p /data

# Expose port 5000
EXPOSE 5000

# Create a non-root user
RUN adduser --disabled-password --gecos '' explorer
USER explorer

# Command to run the application
CMD ["flask-file-explorer"]