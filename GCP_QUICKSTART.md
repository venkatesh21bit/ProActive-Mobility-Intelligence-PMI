# Google Cloud Platform - Quick Start Guide

## Setup PostgreSQL (Cloud SQL)

### Create Instance
```powershell
gcloud sql instances create pmi-postgres \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --network=default
```

### Create Database & User
```powershell
# Create database
gcloud sql databases create pmi_db --instance=pmi-postgres

# Create user
gcloud sql users create pmi_user \
    --instance=pmi-postgres \
    --password=YOUR_SECURE_PASSWORD
```

### Enable TimescaleDB
```powershell
# Connect to database
gcloud sql connect pmi-postgres --user=pmi_user --database=pmi_db

# In psql:
CREATE EXTENSION IF NOT EXISTS timescaledb;
\q
```

### Get Connection String
```powershell
gcloud sql instances describe pmi-postgres --format='value(connectionName)'

# Format: PROJECT_ID:REGION:INSTANCE_NAME
# Use in DATABASE_URL:
# postgresql://pmi_user:PASSWORD@/pmi_db?host=/cloudsql/PROJECT_ID:REGION:pmi-postgres
```

---

## Setup Redis (Memorystore)

### Create Instance
```powershell
gcloud redis instances create pmi-redis \
    --size=1 \
    --region=us-central1 \
    --redis-version=redis_7_0 \
    --tier=basic
```

### Get Connection Info
```powershell
gcloud redis instances describe pmi-redis \
    --region=us-central1 \
    --format='value(host,port)'

# Format for REDIS_URL:
# redis://HOST:6379
```

---

## Deploy Backend to Cloud Run

### Build & Deploy
```powershell
cd backend

# Build
gcloud builds submit --tag gcr.io/YOUR_VENDOR_PROJECT_ID/pmi-backend

# Deploy
gcloud run deploy pmi-backend \
    --image gcr.io/YOUR_VENDOR_PROJECT_ID/pmi-backend \
    --region us-central1 \
    --allow-unauthenticated \
    --min-instances 1 \
    --max-instances 10 \
    --cpu 2 \
    --memory 2Gi \
    --add-cloudsql-instances YOUR_PROJECT_ID:us-central1:pmi-postgres
```

### Set Environment Variables
```powershell
gcloud run services update pmi-backend \
    --region us-central1 \
    --update-env-vars \
DATABASE_URL="postgresql://pmi_user:PASSWORD@/pmi_db?host=/cloudsql/PROJECT:REGION:pmi-postgres",\
REDIS_URL="redis://REDIS_HOST:6379",\
SECRET_KEY="YOUR_SECRET_KEY",\
ENVIRONMENT="production"
```

---

## Deploy Frontend

### Build
```powershell
cd frontend
npm run build
```

### Create Bucket & Upload
```powershell
# Create bucket
gsutil mb gs://YOUR_VENDOR_PROJECT_ID-pmi-frontend

# Upload files
gsutil -m cp -r dist/* gs://YOUR_VENDOR_PROJECT_ID-pmi-frontend/

# Make public
gsutil iam ch allUsers:objectViewer gs://YOUR_VENDOR_PROJECT_ID-pmi-frontend

# Configure website
gsutil web set -m index.html gs://YOUR_VENDOR_PROJECT_ID-pmi-frontend
```

### Access URL
```
https://storage.googleapis.com/YOUR_VENDOR_PROJECT_ID-pmi-frontend/index.html
```

---

## Quick Commands

### View Logs
```powershell
# Backend logs
gcloud run services logs read pmi-backend --region us-central1 --limit 100

# Filter errors
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" --limit 50
```

### Check Status
```powershell
# Cloud Run status
gcloud run services describe pmi-backend --region us-central1

# Cloud SQL status
gcloud sql instances describe pmi-postgres

# Redis status
gcloud redis instances describe pmi-redis --region us-central1
```

### Update Backend
```powershell
# Rebuild and redeploy
cd backend
gcloud builds submit --tag gcr.io/YOUR_VENDOR_PROJECT_ID/pmi-backend
gcloud run services update pmi-backend \
    --image gcr.io/YOUR_VENDOR_PROJECT_ID/pmi-backend \
    --region us-central1
```

---

## Costs (Approximate Monthly)

### Development
- Cloud Run: $10-20
- Cloud SQL (db-f1-micro): $10
- Redis (1GB Basic): $35
- Storage: $1
- **Total: ~$56-66/month**

### Production
- Cloud Run: $50-100
- Cloud SQL (db-custom-2-7680): $180
- Redis (5GB Standard): $175
- Storage + CDN: $5-10
- **Total: ~$410-465/month**

---

## Common Issues

### Connection Refused
- Check if Cloud SQL is in same VPC
- Verify `--add-cloudsql-instances` flag
- Test with Cloud SQL Proxy locally

### Redis Connection Failed
- Verify Redis is in same VPC
- Check firewall rules
- Confirm host and port

### 503 Service Unavailable
- Check Cloud Run logs
- Verify environment variables set
- Test /health endpoint

---

## Next Steps

1. ✅ Run `.\deploy-gcp.ps1`
2. ✅ Create Cloud SQL PostgreSQL
3. ✅ Create Redis Memorystore
4. ✅ Deploy backend to Cloud Run
5. ✅ Deploy frontend to Cloud Storage
6. ⬜ Configure custom domain
7. ⬜ Setup Cloud CDN
8. ⬜ Configure monitoring alerts
9. ⬜ Setup Cloud Build triggers

**See [GCP_DEPLOYMENT.md](./GCP_DEPLOYMENT.md) for detailed instructions.**
