# 🚂 Deploy to Railway - Complete Guide

<div align="center">

![Railway](https://img.shields.io/badge/Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)

**Automotive Predictive Maintenance System**

Deploy your full-stack application to Railway in minutes!

[Quick Start](#-quick-start-15-minutes) • [Full Guide](#-complete-deployment-guide) • [Troubleshooting](#-troubleshooting)

</div>

---

## 📚 Documentation Overview

This repository includes complete Railway deployment documentation:

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **RAILWAY_QUICK_START.md** | Deploy in 15 minutes | First-time deployment |
| **RAILWAY_DEPLOYMENT_GUIDE.md** | Comprehensive step-by-step guide | Detailed instructions |
| **RAILWAY_DEPLOYMENT_CHECKLIST.md** | Interactive checklist | During deployment |
| **RAILWAY_TROUBLESHOOTING.md** | Problem-solving guide | When issues occur |
| **RAILWAY_QUICK_REFERENCE.md** | Quick reference card | Quick lookups |
| **RAILWAY_ENV_TEMPLATE.txt** | All environment variables | Configuration |

---

## 🎯 Quick Start (15 Minutes)

### Prerequisites
- GitHub account
- Railway account ([Sign up](https://railway.app))

### Deployment Steps

#### 1️⃣ Push to GitHub (2 min)
```bash
git init
git add .
git commit -m "Deploy to Railway"
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

#### 2️⃣ Create Railway Project (1 min)
1. Go to [railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository

#### 3️⃣ Add PostgreSQL (1 min)
- Click **"+ New"** → **"Database"** → **"PostgreSQL"**

#### 4️⃣ Add Redis (1 min)
- Click **"+ New"** → **"Database"** → **"Redis"**

#### 5️⃣ Deploy Backend (5 min)
1. Click **"+ New"** → **"GitHub Repo"** → Select repo
2. **Settings** → Set **Root Directory**: `backend`
3. **Variables** → Add:
   ```bash
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   REDIS_URL=${{Redis.REDIS_URL}}
   SECRET_KEY=CHANGE-THIS-32-CHARACTER-RANDOM-STRING
   ALLOWED_ORIGINS=https://your-frontend.railway.app
   ```
4. **Settings** → **Networking** → **Generate Domain**
5. **Copy the backend URL** 📋

#### 6️⃣ Deploy Frontend (5 min)
1. Click **"+ New"** → **"GitHub Repo"** → Select same repo
2. **Settings** → Set **Root Directory**: `frontend`
3. **Variables** → Add:
   ```bash
   VITE_API_URL=https://your-backend-from-step-5.railway.app
   ```
4. **Settings** → **Networking** → **Generate Domain**

#### 7️⃣ Update CORS (1 min)
1. Go back to **Backend Service**
2. **Variables** → Update `ALLOWED_ORIGINS` with frontend URL
3. Wait for automatic redeploy

### ✅ Done!
Visit your frontend URL and start using your app!

---

## 📁 Railway Configuration Files

This repository includes the following Railway-specific files:

### Project Root
```
railway.json          # Railway project configuration
Procfile             # Process definition (alternative)
nixpacks.toml        # Nixpacks build configuration (alternative)
```

### Backend Service
```
backend/
├── railway.toml            # Service configuration
├── .env.example            # Environment variables template
├── Dockerfile              # Container definition
└── setup_railway_db.py     # Database initialization script
```

### Frontend Service
```
frontend/
├── railway.toml      # Service configuration
├── .env.example      # Environment variables template
└── Dockerfile        # Container definition
```

---

## 🏗️ Architecture on Railway

```
┌─────────────────────────────────────────────────┐
│            Railway Project                       │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐      ┌──────────────┐        │
│  │   Frontend   │      │   Backend    │        │
│  │   (React)    │─────▶│  (FastAPI)   │        │
│  │   Port: 80   │      │  Port: Auto  │        │
│  └──────────────┘      └──────┬───────┘        │
│                                │                 │
│                        ┌───────┴────────┐       │
│                        │                 │       │
│                 ┌──────▼──────┐  ┌──────▼─────┐│
│                 │  PostgreSQL │  │   Redis    ││
│                 │   Database  │  │   Cache    ││
│                 └─────────────┘  └────────────┘│
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## 🔧 Environment Variables Setup

### Backend Required Variables

```bash
# Database (Auto-configured by Railway)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis (Auto-configured by Railway)
REDIS_URL=${{Redis.REDIS_URL}}

# Security (YOU MUST CHANGE THIS!)
SECRET_KEY=your-random-32-character-secret-key

# CORS (Update after frontend deployment)
ALLOWED_ORIGINS=https://your-frontend.railway.app

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Frontend Required Variables

```bash
# Backend API (Update with your backend URL)
VITE_API_URL=https://your-backend.railway.app

# Application
VITE_ENVIRONMENT=production
```

### Generate Secret Key

**Linux/Mac:**
```bash
openssl rand -hex 32
```

**Windows PowerShell:**
```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

---

## 🗄️ Database Initialization

### Option 1: Using Railway CLI (Recommended)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and link project
railway login
railway link

# Select backend service
railway service

# Initialize database
railway run python setup_railway_db.py
```

### Option 2: Using Custom Start Command

1. Go to **Backend Service** → **Settings**
2. **Deploy** → **Custom Start Command**
3. Set:
   ```bash
   python setup_railway_db.py && uvicorn api.ingestion_service:app --host 0.0.0.0 --port $PORT
   ```
4. After first successful deployment, revert to:
   ```bash
   uvicorn api.ingestion_service:app --host 0.0.0.0 --port $PORT
   ```

---

## 🧪 Testing Your Deployment

### 1. Backend Health Check
```bash
curl https://your-backend.railway.app/health
```
Expected response:
```json
{"status": "healthy"}
```

### 2. API Documentation
Visit: `https://your-backend.railway.app/docs`

### 3. Frontend Application
Visit: `https://your-frontend.railway.app`

### 4. Database Connection
```bash
railway run python -c "from data.database import AsyncSessionLocal; print('Connected!')"
```

---

## 🔐 Security Checklist

- [ ] Change `SECRET_KEY` from default
- [ ] Set `ALLOWED_ORIGINS` to specific frontend domain
- [ ] Remove any hardcoded credentials
- [ ] Verify HTTPS is enabled (automatic with Railway)
- [ ] Review database password (Railway auto-generates)
- [ ] Don't commit `.env` files to git

---

## 💰 Cost Estimation

Railway uses usage-based pricing:

| Component | Estimated Cost/Month |
|-----------|---------------------|
| Backend Service | $5-10 |
| Frontend Service | $5-10 |
| PostgreSQL Database | $5 |
| Redis Instance | $5 |
| **Total** | **~$20-30/month** |

**Plans:**
- **Hobby**: $5/month (512MB RAM)
- **Pro**: $20/month (8GB RAM)
- **Team**: Custom pricing

---

## 📊 Monitoring

### View Logs
1. Go to any service
2. Click **"Deployments"**
3. Click on active deployment
4. View real-time logs

### Check Metrics
1. Click **"Metrics"** tab
2. Monitor:
   - CPU usage
   - Memory usage
   - Network traffic

### Health Checks
Railway automatically monitors:
- Backend: `/health` endpoint
- Frontend: `/` endpoint

---

## 🚀 Deployment Updates

### Automatic Deployment
Railway automatically deploys when you push to GitHub:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Railway will:
1. Detect the push
2. Build new images
3. Deploy updated services
4. Run health checks

### Manual Deployment
1. Go to service in Railway dashboard
2. Click **"Deployments"**
3. Click **"Deploy"** button

### Rollback
1. Go to **"Deployments"**
2. Find previous working deployment
3. Click **"Redeploy"**

---

## 🌐 Custom Domains (Optional)

### Add Custom Domain

1. Go to service → **Settings** → **Networking**
2. Click **"Custom Domain"**
3. Enter your domain (e.g., `app.yourdomain.com`)
4. Add CNAME record to your DNS:
   ```
   Type: CNAME
   Name: app
   Value: [provided-by-railway].railway.app
   ```

### Update Environment Variables

After adding custom domains:

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

### Common Issues

**Backend won't start:**
- Check environment variables are set
- Verify database connection
- Review deployment logs

**CORS errors:**
- Update `ALLOWED_ORIGINS` in backend
- Ensure no trailing slashes in URLs
- Clear browser cache

**Database connection failed:**
- Ensure PostgreSQL service is running
- Check `DATABASE_URL` reference syntax
- Wait for database to initialize

**Build fails:**
- Verify root directory is set
- Check Dockerfile exists
- Review build logs

For detailed solutions, see [RAILWAY_TROUBLESHOOTING.md](./RAILWAY_TROUBLESHOOTING.md)

---

## 📞 Support

### Railway Resources
- **Docs**: https://docs.railway.app
- **Discord**: https://discord.gg/railway (Most helpful!)
- **Status**: https://status.railway.app
- **Feedback**: https://feedback.railway.app

### Repository Documentation
- Full Deployment Guide: [RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md)
- Troubleshooting: [RAILWAY_TROUBLESHOOTING.md](./RAILWAY_TROUBLESHOOTING.md)
- Quick Reference: [RAILWAY_QUICK_REFERENCE.md](./RAILWAY_QUICK_REFERENCE.md)

---

## 📝 Deployment Checklist

Use [RAILWAY_DEPLOYMENT_CHECKLIST.md](./RAILWAY_DEPLOYMENT_CHECKLIST.md) to track your progress:

- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] PostgreSQL added
- [ ] Redis added
- [ ] Backend deployed
- [ ] Frontend deployed
- [ ] Environment variables configured
- [ ] CORS updated
- [ ] Database initialized
- [ ] Testing complete

---

## 🎉 Success!

Once deployed, you'll have:

✅ Backend API running on Railway  
✅ Frontend app accessible via public URL  
✅ PostgreSQL database for persistent storage  
✅ Redis for caching and real-time features  
✅ Automatic deployments from GitHub  
✅ HTTPS enabled by default  
✅ Monitoring and logs available  

**Your Application URLs:**
- Frontend: `https://[your-service].railway.app`
- Backend: `https://[your-service].railway.app`
- API Docs: `https://[your-backend].railway.app/docs`

---

## 🆚 Railway vs GCP

| Feature | Railway | GCP |
|---------|---------|-----|
| Setup Time | 15 minutes | 1-2 hours |
| Configuration | Simple UI | Complex YAML |
| Database | One-click | Manual setup |
| Pricing | Simple usage-based | Complex pay-as-you-go |
| Learning Curve | Easy | Steep |
| Best For | Small-medium apps | Enterprise scale |

---

## 📄 License

This project is licensed under the MIT License.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

<div align="center">

**Built with ❤️ for Railway Deployment**

[Quick Start](#-quick-start-15-minutes) • [Documentation](#-documentation-overview) • [Support](#-support)

**Ready to deploy? Let's go! 🚀**

</div>
