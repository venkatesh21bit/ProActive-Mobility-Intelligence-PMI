# Production Deployment Guide

## Overview
This guide covers deploying the ProActive Mobility Intelligence platform to production.

## Prerequisites

### Required Tools
- Docker 20+
- Google Cloud SDK
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### Required Accounts
- Google Cloud Platform account
- Firebase account (for frontend hosting)
- GitHub account (for CI/CD)

## Architecture

### Components
1. **Backend API** - FastAPI application on Cloud Run
2. **Frontend** - React SPA on Firebase Hosting
3. **Mobile App** - React Native Expo app
4. **Database** - PostgreSQL on Cloud SQL
5. **Cache/Queue** - Redis (optional)

### Infrastructure Diagram
```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Mobile    │────▶│  Cloud Run   │────▶│  Cloud SQL   │
│     App     │     │   (Backend)  │     │ (PostgreSQL) │
└─────────────┘     └──────────────┘     └──────────────┘
                           │
┌─────────────┐            │
│   Web UI    │────────────┘
│  (Firebase) │
└─────────────┘
```

## Step 1: Database Setup

### Create Cloud SQL Instance
```bash
# Create PostgreSQL instance
gcloud sql instances create pmi-postgres \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=YOUR_SECURE_PASSWORD

# Create database
gcloud sql databases create automotive_db \
  --instance=pmi-postgres

# Create user
gcloud sql users create pmi_user \
  --instance=pmi-postgres \
  --password=YOUR_SECURE_PASSWORD
```

### Apply Migrations
```bash
cd backend

# Set database URL
export DATABASE_URL="postgresql+asyncpg://pmi_user:PASSWORD@/automotive_db?host=/cloudsql/PROJECT:us-central1:pmi-postgres"

# Run migrations
python migrations/apply_migrations.py
```

## Step 2: Backend Deployment

### Build Docker Image
```bash
cd backend

# Build
docker build -t gcr.io/YOUR_PROJECT_ID/pmi-backend .

# Push to GCR
docker push gcr.io/YOUR_PROJECT_ID/pmi-backend
```

### Deploy to Cloud Run
```bash
gcloud run deploy pmi-backend \
  --image gcr.io/YOUR_PROJECT_ID/pmi-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 600 \
  --min-instances 1 \
  --max-instances 10 \
  --set-env-vars "ENVIRONMENT=production,DATABASE_URL=..." \
  --add-cloudsql-instances PROJECT:us-central1:pmi-postgres
```

### Configure Environment Variables
Required environment variables:
```bash
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://...
JWT_SECRET_KEY=<generate-secure-key>
TWILIO_ACCOUNT_SID=<your-twilio-sid>
TWILIO_AUTH_TOKEN=<your-twilio-token>
TWILIO_PHONE_NUMBER=<your-twilio-number>
ALLOWED_HOSTS=your-domain.com,*.your-domain.com
RATE_LIMIT_PER_MINUTE=120
```

## Step 3: Frontend Deployment

### Build and Deploy
```bash
cd frontend

# Install dependencies
npm install

# Build
VITE_API_URL=https://your-backend-url.run.app npm run build

# Deploy to Firebase
firebase deploy --only hosting
```

### Configure Firebase
1. Create Firebase project
2. Enable Hosting
3. Update `frontend/.firebaserc` with your project ID
4. Configure custom domain (optional)

## Step 4: Mobile App Deployment

### Build Android APK
```bash
cd mobile

# Install dependencies
npm install

# Build
expo build:android
```

### Build iOS App
```bash
cd mobile

# Build
expo build:ios
```

### Publish Updates
```bash
# Publish OTA update
expo publish
```

## Step 5: CI/CD Setup

### GitHub Actions
1. Add secrets to GitHub repository:
   - `GCP_PROJECT_ID`
   - `GCP_SA_KEY` (service account JSON)
   - `FIREBASE_TOKEN`
   - `VITE_API_URL`

2. Push to main branch triggers automatic deployment

### Manual Deployment
```bash
# Backend
./deploy-backend.ps1

# Frontend
./deploy-frontend.ps1
```

## Step 6: Monitoring Setup

### Cloud Monitoring
```bash
# Enable Cloud Monitoring
gcloud services enable monitoring.googleapis.com

# Create alerts
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-threshold-value=10 \
  --condition-threshold-duration=300s
```

### Health Checks
- Liveness: `/health/live`
- Readiness: `/health/ready`
- Detailed: `/monitoring/health`

### Metrics Endpoints
- System metrics: `/monitoring/metrics`
- Database stats: `/monitoring/stats/database`
- Performance: `/monitoring/stats/performance`

## Step 7: Security Configuration

### SSL/TLS
Cloud Run automatically provides HTTPS.

### CORS
Configure in `backend/api/ingestion_service.py`:
```python
allowed_origins = [
    "https://your-domain.com",
    "https://www.your-domain.com"
]
```

### Rate Limiting
Configured via environment variable:
```bash
RATE_LIMIT_PER_MINUTE=120
```

### Authentication
- JWT tokens with 30-minute expiry
- Refresh tokens with 7-day expiry
- Password hashing with bcrypt

## Step 8: Backup Strategy

### Database Backups
```bash
# Enable automatic backups
gcloud sql instances patch pmi-postgres \
  --backup-start-time=03:00 \
  --enable-bin-log

# Manual backup
gcloud sql backups create \
  --instance=pmi-postgres \
  --description="Manual backup $(date +%Y-%m-%d)"
```

### Restore from Backup
```bash
gcloud sql backups restore BACKUP_ID \
  --backup-instance=pmi-postgres \
  --backup-id=BACKUP_ID
```

## Step 9: Scaling Configuration

### Auto-scaling
Cloud Run automatically scales based on:
- CPU utilization
- Request concurrency
- Custom metrics

### Manual Scaling
```bash
# Update instance limits
gcloud run services update pmi-backend \
  --min-instances 2 \
  --max-instances 20 \
  --region us-central1
```

## Step 10: Maintenance

### Update Backend
```bash
# Build new version
docker build -t gcr.io/PROJECT/pmi-backend:v2 .

# Deploy with zero downtime
gcloud run deploy pmi-backend \
  --image gcr.io/PROJECT/pmi-backend:v2 \
  --no-traffic

# Gradually migrate traffic
gcloud run services update-traffic pmi-backend \
  --to-revisions=v2=50,v1=50

# Full migration
gcloud run services update-traffic pmi-backend \
  --to-latest
```

### Database Migrations
```bash
# Apply new migrations
python backend/migrations/apply_migrations.py
```

### Rollback
```bash
# Rollback to previous revision
gcloud run services update-traffic pmi-backend \
  --to-revisions=PREVIOUS_REVISION=100
```

## Troubleshooting

### Check Logs
```bash
# Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision" \
  --limit 50 \
  --format json

# Real-time logs
gcloud run services logs read pmi-backend \
  --follow \
  --region us-central1
```

### Debug Database
```bash
# Connect to Cloud SQL
gcloud sql connect pmi-postgres --user=postgres
```

### Health Check
```bash
# Check service health
curl https://your-backend-url.run.app/monitoring/health
```

## Performance Optimization

### Database
- Indexes on frequently queried columns
- Connection pooling (pool_size=20)
- Query optimization
- Regular VACUUM and ANALYZE

### API
- Response caching with Redis
- GZip compression
- Request rate limiting
- Database query batching

### Frontend
- Code splitting
- Lazy loading
- Image optimization
- CDN for static assets

## Cost Optimization

### Cloud Run
- Use min-instances=0 for dev
- Use min-instances=1+ for production
- Monitor and adjust based on traffic

### Cloud SQL
- Use appropriate tier (db-f1-micro for low traffic)
- Scale up during high traffic
- Enable automatic storage increase

### Monitoring
- Set up budget alerts
- Review costs monthly
- Optimize resource usage

## Security Checklist

- [ ] Environment variables secured
- [ ] Database backups enabled
- [ ] SSL/TLS configured
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] JWT secret key strong and unique
- [ ] Passwords hashed with bcrypt
- [ ] SQL injection protection (parameterized queries)
- [ ] Input validation on all endpoints
- [ ] Error messages don't leak sensitive info
- [ ] Logging excludes sensitive data
- [ ] Regular security updates
- [ ] Monitoring and alerting configured

## Support

For issues:
1. Check logs first
2. Review health endpoints
3. Check GitHub Issues
4. Contact support team

## Next Steps

1. Set up monitoring dashboards
2. Configure alerting rules
3. Implement log aggregation
4. Add error tracking (Sentry)
5. Set up A/B testing
6. Implement analytics
7. Add performance monitoring
8. Create incident response plan
