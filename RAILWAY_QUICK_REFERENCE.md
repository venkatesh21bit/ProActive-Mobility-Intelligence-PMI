# 🎴 Railway Deployment - Quick Reference Card

## 📦 Files Created for Railway Deployment

```
├── railway.json                        # Project configuration
├── Procfile                            # Process definition
├── nixpacks.toml                       # Build configuration
├── backend/
│   ├── railway.toml                    # Backend service config
│   └── .env.example                    # Backend env template
├── frontend/
│   ├── railway.toml                    # Frontend service config
│   └── .env.example                    # Frontend env template
└── Documentation/
    ├── RAILWAY_DEPLOYMENT_GUIDE.md     # Full deployment guide
    ├── RAILWAY_QUICK_START.md          # 15-min quick start
    ├── RAILWAY_TROUBLESHOOTING.md      # Problem solving
    ├── RAILWAY_DEPLOYMENT_CHECKLIST.md # Step-by-step checklist
    └── RAILWAY_ENV_TEMPLATE.txt        # All env vars in one place
```

---

## 🚀 Deployment Order

```
1. PostgreSQL → Add database
2. Redis      → Add Redis
3. Backend    → Deploy with DB & Redis
4. Frontend   → Deploy with Backend URL
5. Update     → Fix CORS in Backend
```

---

## 🔑 Critical Environment Variables

### Backend (Minimum Required)
```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
SECRET_KEY=random-32-char-string
ALLOWED_ORIGINS=https://frontend.railway.app
```

### Frontend (Minimum Required)
```bash
VITE_API_URL=https://backend.railway.app
```

---

## 🎯 Service Configuration

### Backend Service
- **Root Directory**: `backend`
- **Build**: Dockerfile
- **Port**: Auto (Railway sets $PORT)
- **Health Check**: `/health`

### Frontend Service
- **Root Directory**: `frontend`
- **Build**: Dockerfile  
- **Port**: 80
- **Health Check**: `/`

---

## ⚡ Quick Commands

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

# Run command
railway run <command>

# Deploy
railway up
```

### Generate Secret Key
```bash
# Linux/Mac
openssl rand -hex 32

# Windows
[Convert]::ToBase64String((1..32|%{Get-Random -Max 256}))
```

---

## 🔗 Important URLs

### After Deployment
```
Frontend:  https://[service-name].railway.app
Backend:   https://[service-name].railway.app
API Docs:  https://[backend].railway.app/docs
Health:    https://[backend].railway.app/health
```

### Railway Resources
- **Dashboard**: https://railway.app/dashboard
- **Docs**: https://docs.railway.app
- **Discord**: https://discord.gg/railway
- **Status**: https://status.railway.app

---

## 🐛 Common Quick Fixes

### CORS Error
```bash
# Update backend variable
ALLOWED_ORIGINS=https://your-frontend.railway.app
```

### Can't Connect to Backend
```bash
# Update frontend variable
VITE_API_URL=https://your-backend.railway.app
```

### Service Won't Start
1. Check logs in Railway dashboard
2. Verify all environment variables set
3. Ensure root directory configured
4. Check database connection

### Build Fails
1. Check root directory setting
2. Verify Dockerfile exists
3. Check build logs for errors
4. Ensure all dependencies in requirements.txt

---

## 📊 Cost Estimate

| Component | Est. Cost/Month |
|-----------|-----------------|
| Backend   | $5-10          |
| Frontend  | $5-10          |
| PostgreSQL| $5             |
| Redis     | $5             |
| **Total** | **$20-30**     |

---

## ✅ Pre-Deploy Checklist

- [ ] Code pushed to GitHub
- [ ] No secrets in code
- [ ] Railway account ready
- [ ] All required files present

---

## 🎯 Success Indicators

✅ Backend deploys successfully
✅ Frontend deploys successfully  
✅ Health check returns 200
✅ API docs accessible
✅ Frontend loads
✅ No CORS errors
✅ API calls work

---

## 📝 Template: Service Reference Syntax

When referencing another Railway service:

```bash
# Format
${{ServiceName.VARIABLE_NAME}}

# Examples
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
BACKEND_URL=${{backend.RAILWAY_PUBLIC_DOMAIN}}
```

---

## 🔧 Root Directory Settings

| Service  | Root Directory |
|----------|----------------|
| Backend  | `backend`      |
| Frontend | `frontend`     |

⚠️ **Critical**: Set this in Service → Settings → Build

---

## 📞 Emergency Contacts

**Railway Down?**
- Check: https://status.railway.app
- Discord: https://discord.gg/railway

**Issue Persists?**
- Review logs
- Check troubleshooting guide
- Ask in Railway Discord

---

## 🎉 Quick Test URLs

After deployment, test these:

```bash
# Backend health
curl https://your-backend.railway.app/health

# Backend API docs
https://your-backend.railway.app/docs

# Frontend
https://your-frontend.railway.app

# Test API call
curl https://your-backend.railway.app/api/health
```

---

**Save this file for quick reference during deployment!**
