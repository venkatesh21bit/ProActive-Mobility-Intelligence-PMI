# Google Cloud Platform Deployment Guide

## ProActive Mobility Intelligence - GCP Deployment

This guide covers deploying the complete system to Google Cloud Platform using your Vendor project.

---

## 📋 Prerequisites

### Required Tools
- Google Cloud SDK (gcloud CLI)
- Docker
- Node.js 20+
- Python 3.11+

### GCP Account Setup
1. **Google Cloud Account** with billing enabled
2. **Project**: Use your existing "Vendor" project
3. **Permissions**: Owner or Editor role

### Install Google Cloud SDK

**Windows (PowerShell):**
```powershell
# Download and install
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe
```

**After installation:**
```powershell
# Initialize gcloud
gcloud init

# Login
gcloud auth login

# Set project
gcloud config set project YOUR_VENDOR_PROJECT_ID
```

---

## 🗂️ GCP Services Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Cloud Load Balancer                   │
│                  (HTTPS, SSL Certificate)                │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐       ┌────────▼───────┐
│   Cloud CDN    │       │   Cloud Run    │
│   (Frontend)   │       │   (Backend)    │
│  Cloud Storage │       │  Auto-scaling  │
└────────────────┘       └────────┬───────┘
                                  │
                    ┌─────────────┴──────────────┐
                    │                            │
            ┌───────▼────────┐         ┌─────────▼────────┐
            │  Cloud SQL     │         │  Memorystore     │
            │  (PostgreSQL)  │         │     (Redis)      │
            │  TimescaleDB   │         │   Stream Cache   │
            └────────────────┘         └──────────────────┘
```

---

## 🚀 Quick Deployment

### Option 1: Automated Deployment Script

```powershell
# Run the deployment script
.\deploy-gcp.ps1
```

Select from menu:
1. Deploy Backend to Cloud Run ✅ **Recommended**
2. Deploy Backend to App Engine
3. Setup Cloud SQL (PostgreSQL)
4. Setup Redis (Memorystore)
5. Deploy Frontend to Cloud Storage + CDN
6. Full Setup (All services)

---

## 📦 Step-by-Step Manual Deployment

### Step 1: Enable Required APIs

```powershell
# Set your project
gcloud config set project YOUR_VENDOR_PROJECT_ID

# Enable APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable sql-component.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable redis.googleapis.com
gcloud services enable storage.googleapis.com
```

---

### Step 2: Create Cloud SQL PostgreSQL Database

**Create Instance:**
```powershell
gcloud sql instances create pmi-postgres \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --network=default \
    --backup \
    --enable-bin-log
```

**Upgrade tier for production:**
```powershell
# For production, use:
# --tier=db-custom-2-7680  (2 vCPU, 7.5GB RAM)
```

**Create Database:**
```powershell
gcloud sql databases create pmi_db --instance=pmi-postgres
```

**Create User:**
```powershell
gcloud sql users create pmi_user \
    --instance=pmi-postgres \
    --password=YOUR_SECURE_PASSWORD
```

**Get Connection Name:**
```powershell
gcloud sql instances describe pmi-postgres \
    --format='value(connectionName)'
```

**Connection String Format:**
```
postgresql://pmi_user:PASSWORD@/pmi_db?host=/cloudsql/PROJECT_ID:REGION:pmi-postgres
```

**Enable TimescaleDB Extension:**
```powershell
# Connect to Cloud SQL
gcloud sql connect pmi-postgres --user=pmi_user --database=pmi_db

# In psql prompt:
CREATE EXTENSION IF NOT EXISTS timescaledb;
```

---

### Step 3: Create Redis Memorystore

**Create Redis Instance:**
```powershell
gcloud redis instances create pmi-redis \
    --size=1 \
    --region=us-central1 \
    --redis-version=redis_7_0 \
    --network=default \
    --tier=basic
```

**For production (high availability):**
```powershell
# Use standard tier with replicas
gcloud redis instances create pmi-redis \
    --size=5 \
    --region=us-central1 \
    --redis-version=redis_7_0 \
    --network=default \
    --tier=standard \
    --replica-count=1
```

**Get Redis Host and Port:**
```powershell
gcloud redis instances describe pmi-redis \
    --region=us-central1 \
    --format='value(host,port)'
```

**Connection String Format:**
```
redis://REDIS_HOST:6379
```

---

### Step 4: Deploy Backend to Cloud Run

**Build and Deploy:**
```powershell
cd backend

# Build container image
gcloud builds submit --tag gcr.io/YOUR_VENDOR_PROJECT_ID/pmi-backend

# Deploy to Cloud Run
gcloud run deploy pmi-backend \
    --image gcr.io/YOUR_VENDOR_PROJECT_ID/pmi-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --min-instances 1 \
    --max-instances 10 \
    --cpu 2 \
    --memory 2Gi \
    --timeout 300 \
    --port 8000 \
    --set-env-vars ENVIRONMENT=production \
    --add-cloudsql-instances YOUR_PROJECT_ID:us-central1:pmi-postgres
```

**Set Environment Variables:**
```powershell
gcloud run services update pmi-backend \
    --region us-central1 \
    --update-env-vars \
DATABASE_URL="postgresql://pmi_user:PASSWORD@/pmi_db?host=/cloudsql/PROJECT_ID:REGION:pmi-postgres",\
REDIS_URL="redis://REDIS_HOST:6379",\
SECRET_KEY="YOUR_SECRET_KEY",\
CORS_ORIGINS="https://yourdomain.com",\
ENVIRONMENT="production"
```

**Get Backend URL:**
```powershell
gcloud run services describe pmi-backend \
    --region us-central1 \
    --format='value(status.url)'
```

---

### Step 5: Deploy Frontend to Cloud Storage + CDN

**Build Frontend:**
```powershell
cd frontend

# Update .env.production with Cloud Run backend URL
# VITE_API_URL=https://pmi-backend-xxx.run.app

npm run build
```

**Create Storage Bucket:**
```powershell
# Bucket name must be globally unique
gsutil mb -p YOUR_VENDOR_PROJECT_ID -c STANDARD -l us-central1 gs://YOUR_VENDOR_PROJECT_ID-pmi-frontend
```

**Upload Files:**
```powershell
gsutil -m cp -r dist/* gs://YOUR_VENDOR_PROJECT_ID-pmi-frontend/
```

**Make Bucket Public:**
```powershell
gsutil iam ch allUsers:objectViewer gs://YOUR_VENDOR_PROJECT_ID-pmi-frontend
```

**Configure Website:**
```powershell
gsutil web set -m index.html -e index.html gs://YOUR_VENDOR_PROJECT_ID-pmi-frontend
```

**Access URL:**
```
https://storage.googleapis.com/YOUR_VENDOR_PROJECT_ID-pmi-frontend/index.html
```

**Optional: Setup Cloud CDN with Load Balancer**

1. Create backend bucket:
```powershell
gcloud compute backend-buckets create pmi-frontend-backend \
    --gcs-bucket-name=YOUR_VENDOR_PROJECT_ID-pmi-frontend \
    --enable-cdn
```

2. Create URL map:
```powershell
gcloud compute url-maps create pmi-frontend-lb \
    --default-backend-bucket=pmi-frontend-backend
```

3. Create HTTPS proxy and forwarding rule (requires SSL certificate)

---

### Step 6: Initialize Database

**Connect via Cloud SQL Proxy:**
```powershell
# Download Cloud SQL Proxy
# https://cloud.google.com/sql/docs/postgres/sql-proxy

# Run proxy
.\cloud_sql_proxy.exe -instances=YOUR_PROJECT_ID:us-central1:pmi-postgres=tcp:5432

# In another terminal, run initialization
cd backend
python -c "from data.database import init_db; import asyncio; asyncio.run(init_db())"
```

---

## 🔒 Security Configuration

### 1. Update Backend CORS

Update `backend/.env`:
```bash
CORS_ORIGINS=https://storage.googleapis.com,https://yourdomain.com
ALLOWED_HOSTS=*.run.app,yourdomain.com
```

### 2. Cloud SQL Security

```powershell
# Enable SSL
gcloud sql instances patch pmi-postgres \
    --require-ssl

# Configure authorized networks (if not using Cloud SQL Proxy)
gcloud sql instances patch pmi-postgres \
    --authorized-networks=YOUR_IP_RANGE
```

### 3. Redis Security

```powershell
# Enable AUTH (Standard tier only)
gcloud redis instances update pmi-redis \
    --region=us-central1 \
    --auth-enabled
```

### 4. IAM Permissions

```powershell
# Create service account for Cloud Run
gcloud iam service-accounts create pmi-backend-sa \
    --display-name="PMI Backend Service Account"

# Grant Cloud SQL client role
gcloud projects add-iam-policy-binding YOUR_VENDOR_PROJECT_ID \
    --member="serviceAccount:pmi-backend-sa@YOUR_VENDOR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

# Update Cloud Run to use service account
gcloud run services update pmi-backend \
    --region=us-central1 \
    --service-account=pmi-backend-sa@YOUR_VENDOR_PROJECT_ID.iam.gserviceaccount.com
```

---

## 📊 Monitoring & Logging

### Cloud Logging

**View Logs:**
```powershell
# Backend logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=pmi-backend" --limit 50

# Filter errors
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" --limit 50
```

### Cloud Monitoring

**Create Uptime Check:**
```powershell
# Via Console: Monitoring > Uptime Checks
# Monitor: https://pmi-backend-xxx.run.app/health
```

**Set Alerts:**
- CPU utilization > 80%
- Memory utilization > 90%
- Error rate > 1%
- Response time > 500ms

---

## 💰 Cost Estimation

### Monthly Costs (Production)

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| Cloud Run | 2 vCPU, 2GB RAM, ~2M requests | ~$50-100 |
| Cloud SQL | db-custom-2-7680 (2 vCPU, 7.5GB) | ~$180 |
| Memorystore Redis | 5GB Standard tier | ~$175 |
| Cloud Storage | 10GB + 100GB transfer | ~$5 |
| Cloud Build | 120 builds/month | Free tier |
| **Total** | | **~$410-460/month** |

### Development/Testing

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| Cloud Run | 1 vCPU, 512MB RAM | ~$10-20 |
| Cloud SQL | db-f1-micro | ~$10 |
| Memorystore Redis | 1GB Basic tier | ~$35 |
| Cloud Storage | 1GB | ~$0.50 |
| **Total** | | **~$55-65/month** |

---

## 🔄 CI/CD with Cloud Build

**Create `cloudbuild.yaml`:**
```yaml
steps:
  # Build backend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/pmi-backend', 'backend']
  
  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/pmi-backend']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
    - 'run'
    - 'deploy'
    - 'pmi-backend'
    - '--image=gcr.io/$PROJECT_ID/pmi-backend'
    - '--region=us-central1'
    - '--platform=managed'

images:
  - 'gcr.io/$PROJECT_ID/pmi-backend'
```

**Setup GitHub Trigger:**
```powershell
gcloud builds triggers create github \
    --repo-name=ProActive-Mobility-Intelligence-PMI \
    --repo-owner=venkatesh21bit \
    --branch-pattern="^master$" \
    --build-config=cloudbuild.yaml
```

---

## 🧪 Testing Deployment

### Backend Health Check
```powershell
curl https://pmi-backend-xxx.run.app/health
```

### Database Connection
```powershell
# Test from Cloud Run
gcloud run services update pmi-backend \
    --region=us-central1 \
    --command="python,-c,from data.database import init_db; import asyncio; asyncio.run(init_db())"
```

### Redis Connection
```powershell
# Test Redis connectivity
gcloud redis instances describe pmi-redis --region=us-central1
```

---

## 📱 Mobile App Configuration

Update `mobile/config.js`:
```javascript
production: {
  apiUrl: 'https://pmi-backend-xxx.run.app',
  environment: 'production',
  enableLogging: false,
}
```

---

## 🆘 Troubleshooting

### Cloud Run Issues

**View Logs:**
```powershell
gcloud run services logs read pmi-backend --region=us-central1
```

**Check Service Status:**
```powershell
gcloud run services describe pmi-backend --region=us-central1
```

### Cloud SQL Connection Issues

**Test Connection:**
```powershell
gcloud sql connect pmi-postgres --user=pmi_user
```

**Check Instance Status:**
```powershell
gcloud sql instances describe pmi-postgres
```

### Redis Connection Issues

**Describe Instance:**
```powershell
gcloud redis instances describe pmi-redis --region=us-central1
```

---

## 🎯 Next Steps

1. ✅ Enable GCP APIs
2. ✅ Create Cloud SQL PostgreSQL
3. ✅ Create Redis Memorystore
4. ✅ Deploy backend to Cloud Run
5. ✅ Deploy frontend to Cloud Storage
6. ⬜ Configure custom domain
7. ⬜ Setup SSL certificate
8. ⬜ Configure Cloud CDN
9. ⬜ Setup monitoring alerts
10. ⬜ Configure Cloud Build CI/CD

---

## 📞 Support

- **GCP Documentation**: https://cloud.google.com/docs
- **Cloud Run**: https://cloud.google.com/run/docs
- **Cloud SQL**: https://cloud.google.com/sql/docs
- **Memorystore**: https://cloud.google.com/memorystore/docs

---

**Deployment complete! Your system is now running on Google Cloud Platform.** ☁️
