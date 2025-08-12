#!/bin/bash

# Download database from GitHub using Git LFS at runtime
# This runs AFTER deployment when the container starts

DB_PATH="${RAILWAY_VOLUME_MOUNT_PATH:-/data}"
DB_FILE="$DB_PATH/oncohotspot.db"

echo "Database path: $DB_PATH"
echo "Checking for database at: $DB_FILE"

# Create database directory if it doesn't exist
mkdir -p "$DB_PATH"

# Check if database exists and has data
if [ -f "$DB_FILE" ]; then
    # Check if it's just an empty database
    TABLE_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM sqlite_master WHERE type='table';" 2>/dev/null || echo "0")
    echo "Database exists with $TABLE_COUNT tables"
    
    if [ "$TABLE_COUNT" -gt "2" ]; then
        echo "Database already populated with data"
        ls -lh "$DB_PATH"
        exit 0
    else
        echo "Database exists but is empty, will re-download"
        rm -f "$DB_FILE"
    fi
fi

echo "Downloading database with data from GitHub LFS..."

# Method 1: Direct download using curl (faster, no git needed)
echo "Attempting direct download..."
curl -L -o "$DB_FILE" "https://media.githubusercontent.com/media/aenoriss/OncoHotspot/main/database/oncohotspot.db" || {
    echo "Direct download failed, trying git method..."
    
    # Method 2: Git LFS clone
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
}

# Verify the download
if [ -f "$DB_FILE" ]; then
    FILE_SIZE=$(stat -c%s "$DB_FILE" 2>/dev/null || stat -f%z "$DB_FILE" 2>/dev/null || echo "0")
    echo "Database downloaded. Size: $((FILE_SIZE / 1024 / 1024)) MB"
    
    # Check table count
    TABLE_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM sqlite_master WHERE type='table';" 2>/dev/null || echo "0")
    echo "Database has $TABLE_COUNT tables"
    
    if [ "$TABLE_COUNT" -lt "2" ]; then
        echo "WARNING: Database seems empty or corrupted"
    fi
else
    echo "ERROR: Failed to download database"
    exit 1
fi

# Set proper permissions
chmod 755 "$DB_PATH"
chmod 644 "$DB_FILE" 2>/dev/null || true

echo "Database setup complete!"
ls -lh "$DB_PATH"