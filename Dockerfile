FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better caching
COPY setup.py pyproject.toml README.md ./

# Copy just the requirements file first to leverage Docker cache
COPY src/plugins/requirements.txt /app/src/plugins/requirements.txt

# Install pip and plugin dependencies
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/src/plugins/requirements.txt && \
    pip install --no-cache-dir setuptools requests

# Now copy the source code (except for the requirements.txt which is already in place)
COPY --chown=root:root src ./src/

# Install the application itself
RUN pip install --no-cache-dir .

# Install git and tree commands
RUN apt-get update && apt-get install -y tree git && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user with specific UID/GID 1000
RUN addgroup --gid 1000 nonroot && adduser --uid 1000 --gid 1000 --disabled-password --gecos "" nonroot

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

# Ensure the requirements file is writeable by the nonroot user
RUN chown nonroot:nonroot /app/src/plugins/requirements.txt && \
    chmod 775 /app/src/plugins/requirements.txt

# Expose port 5000
EXPOSE 5000

# Give ownership of the data directory to the nonroot user
RUN chown -R nonroot:nonroot /data
USER nonroot

# Command to run the application using Python's module execution
CMD ["python", "-m", "src"]