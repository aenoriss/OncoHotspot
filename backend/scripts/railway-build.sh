#!/bin/bash

echo "Installing Git LFS..."
apt-get update && apt-get install -y git-lfs

echo "Pulling LFS files (database)..."
git lfs pull

echo "Installing backend dependencies..."
cd backend
npm install

echo "Building backend..."
npm run build

echo "Verifying database exists..."
if [ -f "../database/oncohotspot.db" ]; then
    echo "✅ Database file found!"
    ls -lh ../database/*.db*
    
    echo "Creating database directory in dist..."
    mkdir -p dist/database
    cp -v ../database/*.db* dist/database/
    echo "Database files copied to dist/database/"
    ls -lh dist/database/
else
    echo "❌ Database file not found!"
    echo "Current directory: $(pwd)"
    echo "Parent directory contents:"
    ls -la ../
    echo "Looking for database directory..."
    find .. -name "*.db" -type f 2>/dev/null || echo "No .db files found"
    exit 1
fi