#!/bin/bash
# Fix permissions for the requirements.txt file

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REQ_FILE="${SCRIPT_DIR}/src/plugins/requirements.txt"

echo "Ensuring requirements.txt exists and has proper permissions..."

# Create the file if it doesn't exist
if [ ! -f "$REQ_FILE" ]; then
    echo "Creating requirements.txt file..."
    touch "$REQ_FILE"
fi

# Make the file world-writeable to ensure Docker container can write to it
echo "Setting permissions on $REQ_FILE..."
chmod 666 "$REQ_FILE"

echo "Done! The file should now be writeable by the Docker container." 