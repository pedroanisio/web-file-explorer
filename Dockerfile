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

# Create a non-root user with specific UID 1000 (standard first user on many Linux systems)
RUN adduser --disabled-password --gecos '' --uid 1000 explorer
# Give ownership of the data directory to the explorer user
RUN chown -R explorer:explorer /data
USER explorer

# Command to run the application
CMD ["web-file-explorer"] # Updated command