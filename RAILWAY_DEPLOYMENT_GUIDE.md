# 🚂 Railway Deployment Guide
## Automotive Predictive Maintenance System

This guide will help you deploy your application to Railway in a step-by-step manner.

---

## 📋 Prerequisites

Before you begin, ensure you have:

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Account**: Your code should be in a GitHub repository
3. **Twilio Account** (Optional): For SMS/voice notifications
4. **Command Line Tools**:
   - Git installed
   - Railway CLI (optional): `npm i -g @railway/cli`

---

## 🏗️ Architecture Overview

Your application will be deployed as **3 separate services** on Railway:

1. **Backend Service** - FastAPI application (Port: assigned by Railway)
2. **Frontend Service** - React/Vite application (Port: assigned by Railway)
3. **PostgreSQL Database** - Railway managed database
4. **Redis** - Railway managed Redis instance

---

## 📦 Step 1: Prepare Your Repository

### 1.1 Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Prepare for Railway deployment"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/your-repo.git

# Push to GitHub
git push -u origin main
```

### 1.2 Verify Required Files

Ensure these files exist in your repository:
- ✅ `backend/Dockerfile`
- ✅ `backend/requirements.txt`
- ✅ `backend/railway.toml`
- ✅ `frontend/Dockerfile`
- ✅ `frontend/railway.toml`
- ✅ `backend/.env.example`
- ✅ `frontend/.env.example`

---

## 🚀 Step 2: Create Railway Project

### 2.1 Login to Railway

1. Go to [railway.app](https://railway.app)
2. Click **"Login"** and sign in with GitHub
3. Authorize Railway to access your repositories

### 2.2 Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository
4. Railway will detect your project

---

## 🗄️ Step 3: Add PostgreSQL Database

### 3.1 Add Database Service

1. In your Railway project dashboard, click **"+ New"**
2. Select **"Database"**
3. Choose **"Add PostgreSQL"**
4. Railway will automatically provision a PostgreSQL instance

### 3.2 Note Database Variables

Railway automatically creates these environment variables:
- `PGHOST`
- `PGPORT`
- `PGUSER`
- `PGPASSWORD`
- `PGDATABASE`
- `DATABASE_URL`

You'll reference these in your backend service.

---

## 🔴 Step 4: Add Redis

### 4.1 Add Redis Service

1. In your Railway project dashboard, click **"+ New"**
2. Select **"Database"**
3. Choose **"Add Redis"**
4. Railway will automatically provision a Redis instance

### 4.2 Note Redis Variables

Railway automatically creates these environment variables:
- `REDIS_HOST`
- `REDIS_PORT`
- `REDIS_PASSWORD`
- `REDIS_URL`

---

## 🔧 Step 5: Deploy Backend Service

### 5.1 Create Backend Service

1. Click **"+ New"** in your project
2. Select **"GitHub Repo"**
3. Choose your repository
4. Click **"Add variables"** or go to **Variables** tab

### 5.2 Configure Root Directory

1. Go to **Settings** tab
2. Scroll to **"Build"** section
3. Set **Root Directory** to: `backend`
4. Click **"Save"**

### 5.3 Configure Environment Variables

Click **"Variables"** tab and add these variables:

#### Required Variables:
```bash
# Application
ENVIRONMENT=production
APP_NAME=ProActive Mobility Intelligence
APP_VERSION=1.0.0

# Database (Reference PostgreSQL service)
DATABASE_URL=${{Postgres.DATABASE_URL}}
POSTGRES_HOST=${{Postgres.PGHOST}}
POSTGRES_PORT=${{Postgres.PGPORT}}
POSTGRES_USER=${{Postgres.PGUSER}}
POSTGRES_PASSWORD=${{Postgres.PGPASSWORD}}
POSTGRES_DB=${{Postgres.PGDATABASE}}

# Redis (Reference Redis service)
REDIS_URL=${{Redis.REDIS_URL}}
REDIS_HOST=${{Redis.REDIS_HOST}}
REDIS_PORT=${{Redis.REDIS_PORT}}
REDIS_PASSWORD=${{Redis.REDIS_PASSWORD}}

# Security (CHANGE THESE!)
SECRET_KEY=your-super-secret-key-at-least-32-characters-long-change-this-now
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# CORS (Update after frontend deployment)
ALLOWED_ORIGINS=https://your-frontend.railway.app,http://localhost:5173
```

#### Optional Variables (for full functionality):
```bash
# Twilio (for SMS/Voice notifications)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Telemetry Simulator
NUM_VEHICLES=10
TELEMETRY_INTERVAL_SECONDS=5
FAILURE_PROBABILITY=0.05
```

### 5.4 Deploy Backend

1. Click **"Settings"**
2. Scroll to **"Networking"** section
3. Click **"Generate Domain"** to get a public URL
4. **Note this URL** - you'll need it for the frontend!
   - Example: `https://your-backend.up.railway.app`

The deployment will start automatically. Monitor in the **"Deployments"** tab.

---

## 🎨 Step 6: Deploy Frontend Service

### 6.1 Create Frontend Service

1. Click **"+ New"** in your Railway project
2. Select **"GitHub Repo"**
3. Choose the same repository
4. This will create a second service

### 6.2 Configure Root Directory

1. Go to **Settings** tab
2. Scroll to **"Build"** section
3. Set **Root Directory** to: `frontend`
4. Click **"Save"**

### 6.3 Configure Environment Variables

Click **"Variables"** tab and add:

```bash
# Backend API URL (use the URL from Step 5.4)
VITE_API_URL=https://your-backend.up.railway.app

# App Configuration
VITE_APP_NAME=ProActive Mobility Intelligence
VITE_APP_VERSION=1.0.0
VITE_ENVIRONMENT=production
```

### 6.4 Generate Frontend Domain

1. Click **"Settings"**
2. Scroll to **"Networking"** section
3. Click **"Generate Domain"**
4. **Note this URL** - this is your app URL!
   - Example: `https://your-frontend.up.railway.app`

---

## 🔄 Step 7: Update CORS Settings

### 7.1 Update Backend Environment Variables

1. Go back to your **Backend Service**
2. Click **"Variables"** tab
3. Update the `ALLOWED_ORIGINS` variable with your frontend URL:

```bash
ALLOWED_ORIGINS=https://your-frontend.up.railway.app
```

4. The backend will automatically redeploy

---

## 🗃️ Step 8: Initialize Database

### 8.1 Access Backend Logs

1. Go to your **Backend Service**
2. Click **"Deployments"** tab
3. Click on the latest deployment
4. View logs to ensure successful startup

### 8.2 Run Database Migrations (Optional)

If you need to run migrations or seed data:

#### Option 1: Using Railway CLI
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Select backend service
railway service

# Run migration
railway run python -m alembic upgrade head

# Or seed demo data
railway run python seed_demo.py
```

#### Option 2: Using Railway Dashboard
1. Go to **Backend Service**
2. Click **"Settings"** → **"Deploy"**
3. Under **"Custom Start Command"**, temporarily set:
   ```bash
   python seed_demo.py && uvicorn api.ingestion_service:app --host 0.0.0.0 --port $PORT
   ```
4. After seeding, remove the `python seed_demo.py &&` part

---

## ✅ Step 9: Verify Deployment

### 9.1 Check Backend Health

Visit: `https://your-backend.up.railway.app/health`

You should see:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-04T12:00:00"
}
```

### 9.2 Check Backend API Docs

Visit: `https://your-backend.up.railway.app/docs`

You should see the FastAPI Swagger documentation.

### 9.3 Check Frontend

Visit: `https://your-frontend.up.railway.app`

Your application should load successfully!

---

## 🔐 Step 10: Security Best Practices

### 10.1 Change Default Secrets

Ensure you've changed:
- ✅ `SECRET_KEY` - Use a strong, random 32+ character string
- ✅ `POSTGRES_PASSWORD` - Railway generates this automatically
- ✅ `REDIS_PASSWORD` - Railway generates this automatically

### 10.2 Generate Strong Secret Key

```bash
# On Linux/Mac
openssl rand -hex 32

# On Windows (PowerShell)
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

### 10.3 Configure CORS Properly

Only allow your actual frontend domain:
```bash
ALLOWED_ORIGINS=https://your-frontend.up.railway.app
```

---

## 📊 Step 11: Monitor Your Application

### 11.1 View Logs

1. Go to any service
2. Click **"Deployments"**
3. Click on active deployment
4. View real-time logs

### 11.2 Monitor Metrics

1. Railway provides built-in metrics
2. Click **"Metrics"** tab to see:
   - CPU usage
   - Memory usage
   - Network traffic

### 11.3 Set Up Alerts (Optional)

1. Go to **Project Settings**
2. Configure webhooks for deployment notifications

---

## 🔧 Step 12: Custom Domain (Optional)

### 12.1 Add Custom Domain to Frontend

1. Go to **Frontend Service**
2. Click **"Settings"** → **"Networking"**
3. Click **"Custom Domain"**
4. Enter your domain (e.g., `app.yourdomain.com`)
5. Add the provided CNAME record to your DNS

### 12.2 Add Custom Domain to Backend

1. Go to **Backend Service**
2. Click **"Settings"** → **"Networking"**
3. Click **"Custom Domain"**
4. Enter your domain (e.g., `api.yourdomain.com`)
5. Add the provided CNAME record to your DNS

### 12.3 Update Environment Variables

After adding custom domains, update:

**Backend:**
```bash
ALLOWED_ORIGINS=https://app.yourdomain.com
```

**Frontend:**
```bash
VITE_API_URL=https://api.yourdomain.com
```

---

## 🐛 Troubleshooting

### Issue: Backend Won't Start

**Check:**
1. View logs in Railway dashboard
2. Ensure all required environment variables are set
3. Verify database connection string
4. Check if PORT is set correctly (Railway sets this automatically)

**Solution:**
```bash
# Ensure start command is correct in railway.toml:
startCommand = "uvicorn api.ingestion_service:app --host 0.0.0.0 --port $PORT"
```

### Issue: Database Connection Failed

**Check:**
1. Verify PostgreSQL service is running
2. Check if DATABASE_URL is properly referenced
3. Ensure network connectivity between services

**Solution:**
Make sure you're using the reference syntax:
```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

### Issue: Frontend Can't Connect to Backend

**Check:**
1. Verify `VITE_API_URL` is set correctly
2. Check CORS settings on backend
3. Ensure backend domain is accessible

**Solution:**
1. Update frontend `VITE_API_URL` with correct backend URL
2. Update backend `ALLOWED_ORIGINS` with frontend URL

### Issue: Build Fails

**Check:**
1. View build logs
2. Verify Dockerfile syntax
3. Check if all dependencies are listed in requirements.txt

**Solution:**
- Ensure your Dockerfiles are in the correct directories
- Verify root directory is set correctly in service settings

### Issue: Out of Memory

**Check:**
1. Monitor memory usage in Metrics
2. Check for memory leaks in code

**Solution:**
- Upgrade Railway plan for more resources
- Optimize your application code
- Consider removing heavy ML libraries if not needed

---

## 💰 Cost Estimation

Railway pricing (as of 2026):

| Plan | Price | Resources |
|------|-------|-----------|
| **Hobby** | $5/month | 512 MB RAM, Shared CPU |
| **Pro** | $20/month | 8 GB RAM, Shared CPU |
| **Team** | Custom | Custom resources |

**Estimated costs for this project:**
- Backend Service: ~$5-10/month
- Frontend Service: ~$5-10/month
- PostgreSQL: ~$5/month
- Redis: ~$5/month
- **Total: ~$20-30/month**

---

## 🎯 Quick Reference Commands

### Railway CLI Commands

```bash
# Install CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# View logs
railway logs

# Run command in Railway environment
railway run <command>

# Open dashboard
railway open

# Deploy manually
railway up
```

---

## 📚 Additional Resources

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Vite Docs**: https://vitejs.dev

---

## ✨ Post-Deployment Checklist

- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible
- [ ] Database provisioned and connected
- [ ] Redis provisioned and connected
- [ ] Environment variables configured
- [ ] CORS settings updated
- [ ] Database initialized/migrated
- [ ] Health check endpoint working
- [ ] API documentation accessible
- [ ] Frontend can communicate with backend
- [ ] Secrets changed from defaults
- [ ] Monitoring set up
- [ ] Custom domains configured (optional)

---

## 🎉 Success!

Your Automotive Predictive Maintenance System is now live on Railway!

**Your URLs:**
- Frontend: `https://your-frontend.up.railway.app`
- Backend API: `https://your-backend.up.railway.app`
- API Docs: `https://your-backend.up.railway.app/docs`

---

## 📞 Support

If you encounter issues:
1. Check Railway Dashboard logs
2. Review this guide
3. Consult Railway documentation
4. Contact Railway support via Discord

---

**Last Updated:** January 4, 2026
**Version:** 1.0.0
