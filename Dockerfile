FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY setup.py pyproject.toml README.md ./
COPY src ./src/

# Install dependencies
COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir . # Install the package itself

# Install tree command
RUN apt-get update && apt-get install -y tree && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user and switch to it
RUN addgroup --system nonroot && adduser --system --ingroup nonroot nonroot

# Set environment variables
ENV FLASK_APP=src
ENV FLASK_FILE_EXPLORER_BASE_DIR=/data
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Create a data directory to mount user files
RUN mkdir -p /data

# Expose port 5000
EXPOSE 5000

# Give ownership of the data directory to the nonroot user
RUN chown -R nonroot:nonroot /data
USER nonroot

# Command to run the application using Python's module execution
CMD ["python", "-m", "src"]