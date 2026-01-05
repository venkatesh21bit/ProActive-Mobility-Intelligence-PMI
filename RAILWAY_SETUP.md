# Railway Deployment - Backend Only

## ✅ What's Changed

- **Dockerfile moved to root** - Railway can now find it easily
- **Removed unnecessary files** - Cleaned up frontend Railway configs
- **Simplified setup** - No need to set Root Directory in Railway

## 🚀 Deploy Now

### In Railway Dashboard:

1. **Remove Root Directory Setting**
   - Go to your backend service → Settings
   - Find "Root Directory" field
   - **Clear it completely** (leave empty)
   - Save

2. **Redeploy**
   - Go to Deployments tab
   - Railway should automatically redeploy with the new commit
   - Or click "Redeploy" button

3. **Add Environment Variables** (if not already added)
   ```bash
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   REDIS_URL=${{Redis.REDIS_URL}}
   SECRET_KEY=your-random-32-char-string
   ALLOWED_ORIGINS=https://your-firebase-app.web.app
   ENVIRONMENT=production
   LOG_LEVEL=INFO
   ```

4. **Generate Domain**
   - Settings → Networking → Generate Domain
   - Save the URL for your Firebase frontend

## 📁 Project Structure

```
Project Root/
├── Dockerfile              ← Backend Dockerfile (Railway uses this)
├── backend/                ← Backend code
│   ├── api/
│   ├── data/
│   ├── requirements.txt
│   └── ...
└── frontend/               ← Frontend (deployed on Firebase)
```

## 📖 Full Guide

See [RAILWAY_BACKEND_ONLY.md](./RAILWAY_BACKEND_ONLY.md) for complete instructions.

## ✨ Next Steps

1. Wait for Railway deployment to complete
2. Test health endpoint: `https://your-backend.railway.app/health`
3. Update Firebase frontend with Railway backend URL
4. Test your application!

---

**Having issues?** Check Railway logs in Deployments tab.
