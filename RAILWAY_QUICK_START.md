# 🚀 Railway Quick Start Guide

**Deploy in 15 minutes!**

## Prerequisites
- GitHub account
- Railway account (sign up at railway.app)

## Quick Steps

### 1. Push to GitHub (2 min)
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

### 2. Create Railway Project (1 min)
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository

### 3. Add PostgreSQL (1 min)
1. Click "+ New" → "Database" → "PostgreSQL"
2. Done! Railway auto-configures connection

### 4. Add Redis (1 min)
1. Click "+ New" → "Database" → "Redis"
2. Done! Railway auto-configures connection

### 5. Deploy Backend (5 min)
1. Click "+ New" → "GitHub Repo" → Select your repo
2. Go to "Settings" → Set **Root Directory** to `backend`
3. Go to "Variables" → Add these:

```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
SECRET_KEY=change-this-to-random-32-character-string
ALLOWED_ORIGINS=https://your-frontend.railway.app
```

4. Go to "Settings" → "Networking" → "Generate Domain"
5. **Copy the backend URL!**

### 6. Deploy Frontend (5 min)
1. Click "+ New" → "GitHub Repo" → Select same repo
2. Go to "Settings" → Set **Root Directory** to `frontend`
3. Go to "Variables" → Add:

```bash
VITE_API_URL=https://your-backend-url-from-step-5.railway.app
```

4. Go to "Settings" → "Networking" → "Generate Domain"

### 7. Update CORS (1 min)
1. Go back to backend service
2. Update `ALLOWED_ORIGINS` with your frontend URL
3. Wait for redeploy

## ✅ Done!

Visit your frontend URL and enjoy!

## Need Help?

See [RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md) for detailed instructions.
