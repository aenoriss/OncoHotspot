#!/usr/bin/env node

const https = require('https');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const DB_PATH = process.env.RAILWAY_VOLUME_MOUNT_PATH || '/data';
const DB_FILE = path.join(DB_PATH, 'oncohotspot.db');
const LFS_URL = 'https://media.githubusercontent.com/media/aenoriss/OncoHotspot/main/database/oncohotspot.db';

console.log('=== Database Download Script ===');
console.log('Database path:', DB_FILE);

// Create directory if it doesn't exist
if (!fs.existsSync(DB_PATH)) {
  console.log('Creating directory:', DB_PATH);
  fs.mkdirSync(DB_PATH, { recursive: true });
}

// Check if database exists and has data
if (fs.existsSync(DB_FILE)) {
  try {
    // Check table count
    const tableCount = execSync(`sqlite3 "${DB_FILE}" "SELECT COUNT(*) FROM sqlite_master WHERE type='table';" 2>/dev/null || echo "0"`)
      .toString().trim();
    
    console.log(`Database exists with ${tableCount} tables`);
    
    if (parseInt(tableCount) > 2) {
      console.log('Database already populated with data');
      const stats = fs.statSync(DB_FILE);
      console.log(`Size: ${(stats.size / 1024 / 1024).toFixed(2)} MB`);
      process.exit(0);
    } else {
      console.log('Database exists but is empty, will re-download');
      fs.unlinkSync(DB_FILE);
    }
  } catch (e) {
    console.log('Could not check database, will re-download');
    fs.unlinkSync(DB_FILE);
  }
}

console.log('Downloading database from GitHub LFS...');
console.log('URL:', LFS_URL);

// Download the file
const file = fs.createWriteStream(DB_FILE);

https.get(LFS_URL, (response) => {
  if (response.statusCode === 302 || response.statusCode === 301) {
    // Follow redirect
    https.get(response.headers.location, (response) => {
      const totalSize = parseInt(response.headers['content-length'], 10);
      let downloadedSize = 0;
      
      response.pipe(file);
      
      response.on('data', (chunk) => {
        downloadedSize += chunk.length;
        const percent = ((downloadedSize / totalSize) * 100).toFixed(1);
        process.stdout.write(`\rDownloading: ${percent}% (${(downloadedSize/1024/1024).toFixed(1)}MB / ${(totalSize/1024/1024).toFixed(1)}MB)`);
      });
      
      file.on('finish', () => {
        file.close();
        console.log('\nDownload complete!');
        
        // Verify the download
        if (fs.existsSync(DB_FILE)) {
          const stats = fs.statSync(DB_FILE);
          console.log(`Database size: ${(stats.size / 1024 / 1024).toFixed(2)} MB`);
          
          try {
            const tableCount = execSync(`sqlite3 "${DB_FILE}" "SELECT COUNT(*) FROM sqlite_master WHERE type='table';" 2>/dev/null || echo "0"`)
              .toString().trim();
            console.log(`Database has ${tableCount} tables`);
            
            if (parseInt(tableCount) < 2) {
              console.error('WARNING: Database seems empty or corrupted');
            } else {
              console.log('Database successfully downloaded and verified!');
            }
          } catch (e) {
            console.log('Could not verify database tables');
          }
        }
      });
    });
  } else {
    response.pipe(file);
    
    file.on('finish', () => {
      file.close();
      console.log('Download complete!');
    });
  }
}).on('error', (err) => {
  fs.unlink(DB_FILE, () => {});
  console.error('Download failed:', err.message);
  process.exit(1);
});