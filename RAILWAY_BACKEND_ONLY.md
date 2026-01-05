# 🚂 Railway Backend Deployment - Quick Guide

**Deploy Backend API in 10 Minutes**

---

## 📋 What You'll Deploy

- **Backend API** (FastAPI) - Your main application
- **PostgreSQL** - Database
- **Redis** - Cache and real-time data

**Frontend**: Already deployed on Firebase ✅

---

## 🚀 Step-by-Step Deployment

### 1️⃣ Push Your Code to GitHub (2 min)

```bash
git add .
git commit -m "Railway backend deployment"
git push
```

### 2️⃣ Create Railway Project (1 min)

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository

### 3️⃣ Add PostgreSQL (1 min)

1. Click **"+ New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Done! Railway auto-configures

### 4️⃣ Add Redis (1 min)

1. Click **"+ New"**
2. Select **"Database"** → **"Redis"**
3. Done! Railway auto-configures

### 5️⃣ Configure Backend Service (5 min)

Your backend service should already be created. Now configure it:

#### A. Go to Settings
1. Click on your backend service
2. Go to **Settings** tab
3. In **"Root Directory"** field, leave it **EMPTY** (Dockerfile is at root now)
4. Save if needed

#### B. Add Environment Variables
Go to **Variables** tab and add:

```bash
# Database (Reference PostgreSQL)
# Railway provides DATABASE_URL automatically, but ensure it uses asyncpg
DATABASE_URL=${{Postgres.DATABASE_URL}}

# If above doesn't work, manually construct it:
# DATABASE_URL=postgresql+asyncpg://username:password@host:port/database

# Redis (Reference Redis)
REDIS_URL=${{Redis.REDIS_URL}}

# Security - CHANGE THIS!
SECRET_KEY=CHANGE-ME-TO-RANDOM-32-CHARACTER-STRING

# CORS - Add your Firebase frontend URL
ALLOWED_ORIGINS=https://your-app.web.app

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
```

#### C. Generate Public Domain
1. Go to **Settings** → **Networking**
2. Click **"Generate Domain"**
3. **Save this URL** - you'll need it for Firebase!

---

## 🔑 Generate Secret Key

**Windows PowerShell:**
```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

**Linux/Mac:**
```bash
openssl rand -hex 32
```

---

## ✅ Verify Deployment

### Check Health
```
https://your-backend.railway.app/health
```

Should return:
```json
{"status": "healthy"}
```

### Check API Docs
```
https://your-backend.railway.app/docs
```

---

## 🔄 Update Firebase Frontend

Update your Firebase frontend to point to the new Railway backend:

```javascript
// In your Firebase config
const API_URL = "https://your-backend.railway.app";
```

---

## 🐛 Troubleshooting

### Build Fails
- Check Railway logs in Deployments tab
- Ensure Dockerfile is at project root
- Verify all backend files are committed

### Can't Connect to Database
Make sure you're using the reference syntax:
```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

### CORS Errors
Update `ALLOWED_ORIGINS` with your Firebase URL:
```bash
ALLOWED_ORIGINS=https://your-app.web.app,https://your-app.firebaseapp.com
```

---

## 📊 Cost Estimate

**~$15-20/month total:**
- Backend: $5-10/month
- PostgreSQL: $5/month
- Redis: $5/month

---

## 🎯 Quick Reference

### Your URLs
- **Backend API**: `https://your-service.railway.app`
- **API Docs**: `https://your-service.railway.app/docs`
- **Frontend**: `https://your-app.web.app` (Firebase)

### Railway CLI
```bash
# Install
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# View logs
railway logs

# Run migrations
railway run python -m alembic upgrade head
```

---

## ✨ Success Checklist

- [ ] Backend deployed on Railway
- [ ] PostgreSQL connected
- [ ] Redis connected
- [ ] Health endpoint working
- [ ] API docs accessible
- [ ] Firebase frontend updated with Railway backend URL
- [ ] CORS configured correctly
- [ ] SECRET_KEY changed

---

**Need help?** Join Railway Discord: https://discord.gg/railway

**Last Updated:** January 5, 2026
