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
else
    echo "❌ Database file not found!"
    exit 1
fi