# 🔧 Railway Deployment Troubleshooting Guide

Common issues and their solutions when deploying to Railway.

---

## 🚨 Common Issues

### 1. Backend Won't Start / Keeps Crashing

#### Symptoms:
- Deployment fails
- Service crashes immediately after starting
- Logs show errors

#### Possible Causes & Solutions:

**A. Missing Environment Variables**
```
Error: KeyError: 'DATABASE_URL'
```
**Solution:**
1. Go to Backend Service → Variables
2. Ensure all required variables are set
3. Check syntax: `${{Postgres.DATABASE_URL}}` (not `${Postgres.DATABASE_URL}`)

**B. Database Connection Failed**
```
Error: could not connect to server: Connection refused
```
**Solution:**
1. Ensure PostgreSQL service is running
2. Check if DATABASE_URL references correct service
3. Wait a few minutes for database to fully initialize
4. Verify service linking in Railway

**C. Port Binding Error**
```
Error: [Errno 98] Address already in use
```
**Solution:**
1. Ensure your app uses `$PORT` environment variable
2. Check Dockerfile CMD: `--port ${PORT:-8080}`
3. Railway automatically sets the PORT variable

**D. Redis Connection Failed**
```
Error: Error 111 connecting to redis. Connection refused.
```
**Solution:**
1. Ensure Redis service is running
2. Verify REDIS_URL is set: `${{Redis.REDIS_URL}}`
3. Check Redis service health in Railway dashboard

---

### 2. Frontend Build Fails

#### Symptoms:
- Build fails during deployment
- Errors in build logs

#### Possible Causes & Solutions:

**A. Missing Environment Variables at Build Time**
```
Error: VITE_API_URL is not defined
```
**Solution:**
1. Add environment variables BEFORE deploying
2. Frontend variables must be set during build, not just runtime
3. Ensure variables start with `VITE_` for Vite to include them

**B. Node Version Mismatch**
```
Error: The engine "node" is incompatible
```
**Solution:**
1. Check `package.json` for engine requirements
2. Railway uses Node 20 by default
3. Add to `package.json` if needed:
```json
"engines": {
  "node": ">=18.0.0"
}
```

**C. Out of Memory During Build**
```
Error: JavaScript heap out of memory
```
**Solution:**
1. Upgrade Railway plan for more build resources
2. Or optimize frontend build:
```json
// vite.config.js
export default defineConfig({
  build: {
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            return 'vendor';
          }
        }
      }
    }
  }
})
```

---

### 3. CORS Errors

#### Symptoms:
```
Access to fetch at 'https://backend.railway.app/api' from origin 
'https://frontend.railway.app' has been blocked by CORS policy
```

#### Solution:
1. Update backend `ALLOWED_ORIGINS` variable:
```bash
ALLOWED_ORIGINS=https://your-frontend.railway.app
```
2. Ensure NO trailing slash in URLs
3. Wait for backend to redeploy
4. Clear browser cache

---

### 4. Frontend Can't Connect to Backend

#### Symptoms:
- Network errors in browser console
- API calls fail
- 404 or 502 errors

#### Possible Causes & Solutions:

**A. Wrong Backend URL**
**Solution:**
1. Check frontend `VITE_API_URL` variable
2. Ensure it matches backend's public domain
3. Include `https://` prefix
4. NO trailing slash

**B. Backend Not Deployed**
**Solution:**
1. Check backend deployment status
2. View backend logs for errors
3. Ensure backend health endpoint works: `/health`

**C. Nginx Configuration Issue**
**Solution:**
Verify `nginx.conf` has proper proxy settings (if using proxy)

---

### 5. Database Migration Issues

#### Symptoms:
- Tables don't exist
- Schema errors
- Missing data

#### Solution:

**Option 1: Using Railway CLI**
```bash
# Install CLI
npm i -g @railway/cli

# Login and link
railway login
railway link

# Select backend service
railway service

# Run migrations
railway run python -m alembic upgrade head

# Seed data
railway run python seed_demo.py
```

**Option 2: Using Temporary Start Command**
1. Go to Backend Service → Settings
2. Under "Deploy" → "Custom Start Command"
3. Temporarily set:
```bash
alembic upgrade head && python seed_demo.py && uvicorn api.ingestion_service:app --host 0.0.0.0 --port $PORT
```
4. After first successful deploy, revert to:
```bash
uvicorn api.ingestion_service:app --host 0.0.0.0 --port $PORT
```

**Option 3: Manual Database Access**
1. Get database credentials from Postgres service
2. Use PostgreSQL client to connect
3. Run SQL migrations manually

---

### 6. Service Root Directory Not Set

#### Symptoms:
- Wrong files being built
- Build can't find Dockerfile
- Module import errors

#### Solution:
1. Go to Service → Settings
2. Scroll to "Build" section
3. Set "Root Directory":
   - Backend: `backend`
   - Frontend: `frontend`
4. Redeploy

---

### 7. Environment Variable Not Working

#### Symptoms:
- Variables show as undefined
- Configuration not loading

#### Solutions:

**A. Frontend Variables**
- Must start with `VITE_`
- Set BEFORE build
- Access via `import.meta.env.VITE_API_URL`

**B. Backend Variables**
- Check spelling and case
- Ensure no extra spaces
- Use Railway reference syntax for services: `${{Postgres.DATABASE_URL}}`

**C. Variable Not Updating**
- Redeploy after changing variables
- Check "Variables" tab shows latest values
- Clear any caches

---

### 8. Build/Deploy Takes Too Long

#### Symptoms:
- Build exceeds time limit
- Deployment times out

#### Solutions:

**A. Optimize Dockerfile**
```dockerfile
# Use smaller base image
FROM python:3.11-slim  # Not python:3.11

# Combine RUN commands
RUN apt-get update && apt-get install -y gcc g++ \
    && rm -rf /var/lib/apt/lists/*

# Use build cache effectively
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
```

**B. Reduce Dependencies**
- Remove unused packages from `requirements.txt`
- Use lightweight alternatives
- Comment out heavy ML libraries if not needed

**C. Upgrade Plan**
- Railway Hobby plan has limited resources
- Pro plan offers faster builds

---

### 9. Secret Key Errors

#### Symptoms:
```
Error: SECRET_KEY must be set
Error: Invalid token signature
```

#### Solution:
1. Generate a strong secret key:
```bash
# Linux/Mac
openssl rand -hex 32

# Windows PowerShell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```
2. Add to backend variables:
```bash
SECRET_KEY=your_generated_32_character_string_here
```
3. NEVER commit secret keys to git

---

### 10. Health Check Failing

#### Symptoms:
- Railway marks service as unhealthy
- Service keeps restarting

#### Solution:

**A. Ensure Health Endpoint Exists**
Check your FastAPI app has:
```python
@app.get("/health")
async def health():
    return {"status": "healthy"}
```

**B. Update railway.toml**
```toml
[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 100
```

**C. Check Port**
Ensure app listens on `$PORT` variable

---

## 🔍 Debugging Steps

### Step 1: Check Deployment Logs
1. Go to Service → Deployments
2. Click on latest deployment
3. Read logs carefully
4. Look for error messages

### Step 2: Verify Environment Variables
1. Go to Service → Variables
2. Check all required variables are set
3. Verify reference syntax for service links
4. Ensure no typos

### Step 3: Test Locally
```bash
# Backend
cd backend
docker build -t backend-test .
docker run -p 8080:8080 --env-file .env backend-test

# Frontend
cd frontend
docker build -t frontend-test .
docker run -p 80:80 frontend-test
```

### Step 4: Check Service Health
- Visit backend health endpoint: `https://your-backend.railway.app/health`
- Check API docs: `https://your-backend.railway.app/docs`
- Test frontend: `https://your-frontend.railway.app`

### Step 5: Review Railway Status
- Check Railway status page: https://status.railway.app
- Look for service outages
- Check deployment history

---

## 📞 Getting Help

### Railway Support Channels

1. **Railway Discord** (Best for quick help)
   - https://discord.gg/railway
   - Very active community
   - Railway team members available

2. **Railway Docs**
   - https://docs.railway.app
   - Comprehensive guides

3. **Railway Feedback**
   - https://feedback.railway.app
   - Report bugs and request features

4. **GitHub Discussions**
   - Railway community discussions

### Information to Include When Asking for Help

```
Service: [Backend/Frontend/Database]
Error: [Exact error message]
Deployment ID: [From Railway dashboard]
Steps taken: [What you've already tried]
Logs: [Relevant log excerpts]
```

---

## 🎯 Prevention Checklist

Avoid issues by following these best practices:

- [ ] Test locally with Docker before deploying
- [ ] Use environment variable references correctly
- [ ] Set root directory for each service
- [ ] Configure all required environment variables
- [ ] Use strong, random secret keys
- [ ] Keep dependencies minimal and updated
- [ ] Monitor deployment logs regularly
- [ ] Test after each deployment
- [ ] Keep documentation updated
- [ ] Have a rollback plan

---

## 🚑 Emergency Procedures

### If Production is Down

1. **Check Railway Status**
   - Visit https://status.railway.app
   
2. **Rollback to Previous Deployment**
   - Go to Service → Deployments
   - Find last working deployment
   - Click "Redeploy"

3. **Check Recent Changes**
   - Review recent commits
   - Check recent variable changes
   - Verify no breaking changes

4. **Enable Maintenance Mode** (if applicable)
   - Display maintenance page to users
   - Communicate via status page

5. **Fix and Test Locally**
   - Reproduce issue locally
   - Fix and test
   - Deploy fix

---

**Last Updated:** January 4, 2026
