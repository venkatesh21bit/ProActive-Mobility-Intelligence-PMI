# 🚀 Deploy to Production - NOW!

## Pre-Flight Checklist

Before deploying, ensure you have:

- [ ] Google Cloud Project created
- [ ] Cloud SQL instance running
- [ ] Firebase project created (for frontend)
- [ ] GitHub repository connected
- [ ] Environment variables ready

## 🎯 ONE-COMMAND DEPLOYMENT

### Step 1: Set Environment Variables (One-Time Setup)

```powershell
# Set your GCP project
$env:GCP_PROJECT_ID = "your-project-id"

# Set your database password
$env:DB_PASSWORD = "your-secure-database-password"

# Generate JWT secret
$env:JWT_SECRET = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

### Step 2: Deploy Everything

```powershell
# Navigate to project root
cd "c:\Users\91902\Documents\Other_Projects\Automotive predictive maintenance"

# Deploy backend + database migrations
.\deploy-backend.ps1

# Deploy frontend
.\deploy-frontend.ps1
```

## ⚡ FASTEST PATH TO PRODUCTION

### Option A: Use Existing Deployment (RECOMMENDED)

Your backend is ALREADY deployed! Just update it:

```powershell
cd backend

# Apply new database migrations
gcloud sql connect pmi-postgres --user=postgres --quiet
# Then run: \i migrations/001_add_auth_fields.sql

# Update Cloud Run service with new environment variables
gcloud run services update pmi-backend `
  --region us-central1 `
  --set-env-vars "JWT_SECRET_KEY=$env:JWT_SECRET,ENVIRONMENT=production"

# Restart service
gcloud run services update pmi-backend --region us-central1
```

**Your production backend URL:**
```
https://pmi-backend-418022813675.us-central1.run.app
```

### Option B: Fresh Deployment

```powershell
# 1. Build and deploy backend
cd backend
docker build -t gcr.io/crested-polygon-451704-j6/pmi-backend:v2 .
docker push gcr.io/crested-polygon-451704-j6/pmi-backend:v2

gcloud run deploy pmi-backend `
  --image gcr.io/crested-polygon-451704-j6/pmi-backend:v2 `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated `
  --memory 2Gi `
  --cpu 2 `
  --min-instances 1 `
  --max-instances 10 `
  --set-env-vars "ENVIRONMENT=production,JWT_SECRET_KEY=$env:JWT_SECRET"

# 2. Apply database migrations
python migrations/apply_migrations.py

# 3. Deploy frontend
cd ..\frontend
npm install
npm run build
firebase deploy --only hosting
```

## 🔥 INSTANT VERIFICATION

After deployment, verify immediately:

```powershell
# Test health check
Invoke-WebRequest -Uri "https://pmi-backend-418022813675.us-central1.run.app/monitoring/health" -Method GET

# Expected response: {"status":"healthy",...}

# Test registration
$body = @{
    email = "test@example.com"
    password = "Test123!@#"
    first_name = "Test"
    last_name = "User"
    phone = "+1234567890"
} | ConvertTo-Json

Invoke-WebRequest -Uri "https://pmi-backend-418022813675.us-central1.run.app/api/auth/register" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

## 📱 MOBILE APP SETUP

Update mobile app configuration:

```javascript
// mobile/config.js
export default {
  apiUrl: 'https://pmi-backend-418022813675.us-central1.run.app'
};
```

Then:
```bash
cd mobile
npm install
npm start
```

## 🌐 FRONTEND SETUP

Update frontend API URL:

```javascript
// frontend/src/utils/api.js
const API_BASE_URL = 'https://pmi-backend-418022813675.us-central1.run.app';
```

## 🎉 POST-DEPLOYMENT TASKS

### 1. Create Admin User

```powershell
$adminBody = @{
    email = "admin@yourdomain.com"
    password = "SecureAdminPassword123!"
    first_name = "Admin"
    last_name = "User"
    phone = "+1234567890"
} | ConvertTo-Json

$response = Invoke-WebRequest `
  -Uri "https://pmi-backend-418022813675.us-central1.run.app/api/auth/register" `
  -Method POST `
  -ContentType "application/json" `
  -Body $adminBody

# Then manually update role in database:
gcloud sql connect pmi-postgres --user=postgres
# UPDATE customers SET role = 'admin' WHERE email = 'admin@yourdomain.com';
```

### 2. Set Up Monitoring Alerts

```powershell
# Enable monitoring
gcloud services enable monitoring.googleapis.com

# Create uptime check
gcloud monitoring uptime-checks create pmi-backend-health `
  --resource-type=uptime-url `
  --display-name="PMI Backend Health" `
  --http-check-path="/monitoring/health" `
  --check-interval=60s
```

### 3. Configure Auto-Backup

```powershell
# Enable automated backups
gcloud sql instances patch pmi-postgres `
  --backup-start-time=03:00 `
  --enable-bin-log
```

## ✅ PRODUCTION CHECKLIST

After deployment, verify:

- [ ] Backend health check returns 200 OK
- [ ] Can register new user
- [ ] Can login with credentials
- [ ] JWT tokens are working
- [ ] Database migrations applied
- [ ] Mobile app connects successfully
- [ ] Frontend loads and communicates with backend
- [ ] Monitoring endpoints accessible
- [ ] Auto-scaling configured
- [ ] Backups scheduled

## 🚨 IF SOMETHING GOES WRONG

### Backend Not Responding

```powershell
# Check logs
gcloud run services logs read pmi-backend --limit 50

# Restart service
gcloud run services update pmi-backend --region us-central1

# Check database connection
gcloud sql connect pmi-postgres --user=postgres
```

### Database Issues

```powershell
# Check instance status
gcloud sql instances describe pmi-postgres

# Restart instance
gcloud sql instances restart pmi-postgres
```

### Rollback Deployment

```powershell
# List revisions
gcloud run revisions list --service=pmi-backend

# Rollback to previous
gcloud run services update-traffic pmi-backend `
  --to-revisions=pmi-backend-00047=100
```

## 📊 MONITOR YOUR DEPLOYMENT

### Real-Time Monitoring

```powershell
# Watch logs
gcloud run services logs read pmi-backend --follow

# Check metrics
Invoke-WebRequest -Uri "https://pmi-backend-418022813675.us-central1.run.app/monitoring/metrics"

# Database stats
Invoke-WebRequest -Uri "https://pmi-backend-418022813675.us-central1.run.app/monitoring/stats/database"
```

### Cloud Console Links

- **Cloud Run**: https://console.cloud.google.com/run
- **Cloud SQL**: https://console.cloud.google.com/sql
- **Logs**: https://console.cloud.google.com/logs
- **Monitoring**: https://console.cloud.google.com/monitoring

## 🎯 QUICK TEST SCRIPT

Save this as `test-production.ps1`:

```powershell
$baseUrl = "https://pmi-backend-418022813675.us-central1.run.app"

Write-Host "Testing Production Deployment..." -ForegroundColor Green

# Test 1: Health Check
Write-Host "`n1. Health Check..." -ForegroundColor Yellow
$health = Invoke-WebRequest -Uri "$baseUrl/monitoring/health" -Method GET
Write-Host "✅ Health: $($health.StatusCode)" -ForegroundColor Green

# Test 2: Metrics
Write-Host "`n2. Metrics..." -ForegroundColor Yellow
$metrics = Invoke-WebRequest -Uri "$baseUrl/monitoring/metrics" -Method GET
Write-Host "✅ Metrics: $($metrics.StatusCode)" -ForegroundColor Green

# Test 3: Database Stats
Write-Host "`n3. Database Stats..." -ForegroundColor Yellow
$dbStats = Invoke-WebRequest -Uri "$baseUrl/monitoring/stats/database" -Method GET
$stats = $dbStats.Content | ConvertFrom-Json
Write-Host "✅ Customers: $($stats.total_customers)" -ForegroundColor Green
Write-Host "✅ Vehicles: $($stats.total_vehicles)" -ForegroundColor Green

Write-Host "`n🎉 All tests passed! Production is ready!" -ForegroundColor Green
```

Run it:
```powershell
.\test-production.ps1
```

## 🌟 YOU'RE LIVE!

Your production system is now running at:

- **Backend API**: https://pmi-backend-418022813675.us-central1.run.app
- **API Docs**: https://pmi-backend-418022813675.us-central1.run.app/docs
- **Health Check**: https://pmi-backend-418022813675.us-central1.run.app/monitoring/health

## 📞 SUPPORT

If you need help:

1. Check logs: `gcloud run services logs read pmi-backend`
2. Review documentation: `PRODUCTION_DEPLOYMENT_GUIDE.md`
3. Quick reference: `QUICK_REFERENCE.md`
4. API docs: `API_DOCUMENTATION.md`

## 🎊 CONGRATULATIONS!

Your production-grade system is LIVE! 🚀

---

**Next Steps:**
1. Test all features thoroughly
2. Set up monitoring alerts
3. Configure custom domain (optional)
4. Share with users
5. Monitor performance

**Happy Deploying! 🎉**
