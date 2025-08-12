#!/bin/bash

# Download database from GitHub using Git LFS at runtime
# This runs AFTER deployment when the container starts

DB_PATH="${RAILWAY_VOLUME_MOUNT_PATH:-/app/database}"
DB_FILE="$DB_PATH/oncohotspot.db"

echo "Database path: $DB_PATH"
echo "Checking for database at: $DB_FILE"

# Create database directory if it doesn't exist
mkdir -p "$DB_PATH"

# If database doesn't exist, download it
if [ ! -f "$DB_FILE" ]; then
    echo "Database not found. Downloading from GitHub..."
    
    # Install git-lfs if not present
    if ! command -v git-lfs &> /dev/null; then
        echo "Installing git-lfs..."
        apk add --no-cache git git-lfs || apt-get install -y git-lfs
    fi
    
    # Clone only the database directory with LFS
    cd /tmp
    git lfs install
    
    # Use sparse checkout to only get database files
    git clone --filter=blob:none --sparse https://github.com/aenoriss/OncoHotspot.git temp_repo
    cd temp_repo
    git sparse-checkout set database
    git lfs pull --include="database/*.db*"
    
    # Copy database files to volume
    cp -v database/*.db* "$DB_PATH/"
    
    # Clean up
    cd /
    rm -rf /tmp/temp_repo
    
    echo "Database downloaded successfully!"
    ls -lh "$DB_PATH"
else
    echo "Database already exists at: $DB_FILE"
    ls -lh "$DB_PATH"
fi

# Set proper permissions
chmod 755 "$DB_PATH"
chmod 644 "$DB_FILE" 2>/dev/null || true