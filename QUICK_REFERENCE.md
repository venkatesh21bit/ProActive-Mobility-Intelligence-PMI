# Quick Reference - Production System

## 🚀 Quick Start Commands

### Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
python migrations/apply_migrations.py
uvicorn api.ingestion_service:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Mobile
cd mobile
npm install
npm start
```

### Production Deployment

```bash
# Deploy everything
./deploy-gcp.ps1

# Backend only
./deploy-backend.ps1

# Frontend only
./deploy-frontend.ps1
```

## 📍 Important URLs

### Production
- **Backend API**: https://pmi-backend-418022813675.us-central1.run.app
- **Health Check**: https://pmi-backend-418022813675.us-central1.run.app/monitoring/health
- **API Docs**: https://pmi-backend-418022813675.us-central1.run.app/docs
- **Frontend**: (Your Firebase URL)

### Endpoints
- Health: `/monitoring/health`
- Metrics: `/monitoring/metrics`
- Database Stats: `/monitoring/stats/database`
- Login: `/api/auth/login`
- Register: `/api/auth/register`
- Bookings: `/api/bookings/create`

## 🔑 Environment Variables

### Required for Backend
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
JWT_SECRET_KEY=your-secret-key-here
ENVIRONMENT=production
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=your-number
```

### Optional
```bash
RATE_LIMIT_PER_MINUTE=120
ALLOWED_HOSTS=*
REDIS_HOST=localhost
REDIS_PORT=6379
```

## 🧪 Testing Commands

```bash
# Backend tests
cd backend
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Frontend tests
cd frontend
npm test

# Mobile tests
cd mobile
npm test
```

## 📊 Monitoring Commands

```bash
# Check service health
curl https://YOUR_URL/monitoring/health

# Get system metrics
curl https://YOUR_URL/monitoring/metrics

# Get database stats
curl https://YOUR_URL/monitoring/stats/database

# View logs
gcloud logging read "resource.type=cloud_run_revision" --limit 50

# Follow logs
gcloud run services logs read pmi-backend --follow
```

## 🔧 Database Commands

```bash
# Apply migrations
cd backend
python migrations/apply_migrations.py

# Connect to database
gcloud sql connect pmi-postgres --user=postgres

# Create backup
gcloud sql backups create --instance=pmi-postgres

# List backups
gcloud sql backups list --instance=pmi-postgres
```

## 🐛 Debugging

### Check Backend Logs
```bash
gcloud run services logs read pmi-backend --limit 100
```

### Test Endpoint
```bash
curl -X POST https://YOUR_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'
```

### Database Query
```sql
-- Connect to DB first
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM vehicles;
SELECT COUNT(*) FROM appointments;
```

## 🔄 Common Tasks

### Update Backend
```bash
cd backend
# Make changes
docker build -t gcr.io/PROJECT/pmi-backend .
docker push gcr.io/PROJECT/pmi-backend
gcloud run deploy pmi-backend --image gcr.io/PROJECT/pmi-backend
```

### Rollback Deployment
```bash
gcloud run services update-traffic pmi-backend --to-revisions=PREVIOUS_REVISION=100
```

### Scale Service
```bash
gcloud run services update pmi-backend --min-instances=2 --max-instances=20
```

### Update Environment Variable
```bash
gcloud run services update pmi-backend --set-env-vars "KEY=VALUE"
```

## 📞 API Examples

### Register
```bash
curl -X POST https://YOUR_URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure123",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890"
  }'
```

### Login
```bash
curl -X POST https://YOUR_URL/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure123"
  }'
```

### Create Booking (with auth)
```bash
TOKEN="your-jwt-token"
curl -X POST https://YOUR_URL/api/bookings/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "customer_id": 1,
    "vehicle_id": 1,
    "service_type": "regular_service",
    "preferred_date": "2024-12-25",
    "preferred_time": "10:00"
  }'
```

## 🎯 Health Check Response

```json
{
  "status": "healthy",
  "timestamp": "2024-12-17T12:00:00Z",
  "environment": "production",
  "version": "2.0.0",
  "checks": {
    "database": "healthy",
    "redis": "healthy"
  },
  "uptime_seconds": 86400
}
```

## 🔐 Security Best Practices

1. **Never commit secrets** - Use environment variables
2. **Rotate JWT secret** - Change periodically
3. **Use strong passwords** - Min 8 chars, mixed case
4. **Enable 2FA** - For admin accounts
5. **Monitor logs** - Check for suspicious activity
6. **Update dependencies** - Keep packages current
7. **Backup database** - Daily automated backups
8. **Use HTTPS only** - No plain HTTP

## 📈 Performance Tips

1. **Use indexes** - On frequently queried columns
2. **Connection pooling** - Configure pool_size
3. **Cache responses** - Use Redis for hot data
4. **Compress responses** - GZip enabled
5. **Optimize queries** - Use EXPLAIN ANALYZE
6. **Monitor metrics** - Watch CPU, memory, disk
7. **Scale horizontally** - Add more instances
8. **Use CDN** - For static assets

## 🆘 Troubleshooting

### Service Not Responding
1. Check health endpoint
2. View logs: `gcloud run services logs read pmi-backend`
3. Check database connection
4. Verify environment variables

### Database Connection Error
1. Check Cloud SQL instance status
2. Verify DATABASE_URL format
3. Check firewall rules
4. Test connection: `gcloud sql connect`

### Authentication Failing
1. Verify JWT_SECRET_KEY is set
2. Check token expiration
3. Validate password hash
4. Test login endpoint

### High Memory Usage
1. Check active connections
2. Review connection pool settings
3. Look for memory leaks
4. Scale up instance

## 📚 Documentation Links

- [Production Deployment Guide](./PRODUCTION_DEPLOYMENT_GUIDE.md)
- [API Documentation](./API_DOCUMENTATION.md)
- [Production Ready Summary](./PRODUCTION_READY_SUMMARY.md)
- [Security Guide](./SECURITY.md)
- [GitHub Secrets Setup](./GITHUB_SECRETS_SETUP.md)

## 🎓 Training Resources

- FastAPI: https://fastapi.tiangolo.com/
- Cloud Run: https://cloud.google.com/run/docs
- React: https://react.dev/
- React Native: https://reactnative.dev/

## 📞 Support

- **Technical Issues**: Open GitHub issue
- **Security Issues**: security@example.com
- **General Support**: support@example.com
- **Documentation**: https://docs.example.com

## 🔄 Version History

- **v2.0.0** (2024-12-17) - Production-ready release
  - JWT authentication
  - RBAC implementation
  - Comprehensive monitoring
  - CI/CD pipeline
  - Full documentation

- **v1.0.0** (2024-11-01) - Initial release
  - Basic functionality
  - Simple authentication
  - Core features

---

**Last Updated**: December 17, 2024
**Maintainer**: Development Team
**Status**: Production Ready ✅
