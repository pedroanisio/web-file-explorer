FROM python:3.12-slim

WORKDIR /app

# Install Node.js and npm
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy package files for npm
COPY package*.json ./
RUN npm install

# Copy Tailwind config
COPY tailwind.config.js ./

# Copy requirements first for better caching
COPY setup.py pyproject.toml README.md ./

# Copy just the requirements file first to leverage Docker cache
COPY src/plugins/requirements.txt /app/src/plugins/requirements.txt

# Install pip and plugin dependencies
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/src/plugins/requirements.txt && \
    pip install --no-cache-dir setuptools requests

# Now copy the source code
COPY --chown=root:root src ./src/

# Build Tailwind CSS
RUN npx tailwindcss -i ./src/static/css/tailwind-styles.css -o ./src/static/css/tailwind.css

# Install the application itself
RUN pip install --no-cache-dir .

# Install git, tree, cloc and libmagic
RUN apt-get update && apt-get install -y tree git cloc libmagic1 && \
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

# Ensure the requirements file, templates directory, and static directory are writeable by the nonroot user
RUN chown nonroot:nonroot /app/src/plugins/requirements.txt && \
    chmod 775 /app/src/plugins/requirements.txt && \
    mkdir -p /app/src/templates && \
    chown -R nonroot:nonroot /app/src/templates && \
    chmod -R 775 /app/src/templates && \
    mkdir -p /app/src/static/css && \
    chown -R nonroot:nonroot /app/src/static && \
    chmod -R 775 /app/src/static

# Expose port 5000
EXPOSE 5000

# Give ownership of the data directory to the nonroot user
RUN chown -R nonroot:nonroot /data
USER nonroot

# Command to run the application using Python's module execution
CMD ["python", "-m", "src"]