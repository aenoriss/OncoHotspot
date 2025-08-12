# Railway Deployment with SQLite Database

## Important: Railway Volume Setup Required

Railway doesn't pull Git LFS files during build. To use the SQLite database, you need to set up a Railway Volume.

## Step-by-Step Setup

### 1. Deploy the Service First
1. Connect your GitHub repository to Railway
2. Let it deploy (it will fail initially - this is expected)

### 2. Add a Volume for the Database
1. In your Railway service, go to **Settings** → **Volumes**
2. Click **+ New Volume**
3. Set mount path to: `/data`
4. Click **Add**

### 3. Update Environment Variables
After adding the volume, Railway automatically provides:
- `RAILWAY_VOLUME_MOUNT_PATH` - The path where the volume is mounted

Add this custom variable:
- `DATABASE_PATH` = `${RAILWAY_VOLUME_MOUNT_PATH}/oncohotspot.db`

### 4. Redeploy
1. Go to **Deployments**
2. Click **Redeploy** on the latest deployment
3. The service will:
   - Download the database from GitHub using Git LFS
   - Store it in the persistent volume
   - Start the application

## How It Works

1. **First Deploy**: The `download-database.sh` script checks if the database exists
2. **If Not Found**: Downloads it from GitHub using Git LFS
3. **Stores in Volume**: Saves to the persistent volume at `/data`
4. **Future Deploys**: Database persists in the volume, no re-download needed

## Troubleshooting

### Database Not Found
Check the deploy logs for:
```
Database not found. Downloading from GitHub...
```

### Permission Issues
The script automatically sets permissions, but if you see errors:
```bash
chmod 755 ${RAILWAY_VOLUME_MOUNT_PATH}
chmod 644 ${RAILWAY_VOLUME_MOUNT_PATH}/oncohotspot.db
```

### Volume Not Mounted
Ensure you see this in environment variables:
```
RAILWAY_VOLUME_MOUNT_PATH=/data
```

## Alternative: Use PostgreSQL

Railway provides PostgreSQL databases that work out-of-the-box:
1. Add PostgreSQL service from Railway dashboard
2. Railway automatically provides `DATABASE_URL`
3. Use the migration script in `backend/scripts/migrate-to-postgres.sql`

## Database Info

The SQLite database contains:
- 37,953 mutation records
- 32 TCGA cancer studies  
- 145 genes with therapeutic data
- Size: ~23MB (with WAL files)