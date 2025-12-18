# Deployment script for backend with Auth and Booking APIs
# Run this after starting Docker Desktop

Write-Host "🚀 Deploying Backend with Auth and Booking APIs" -ForegroundColor Cyan
Write-Host "=" * 60

# Check if Docker is running
Write-Host "`n1️⃣  Checking Docker..." -ForegroundColor Yellow
try {
    docker info > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
        Write-Host "   Then run this script again." -ForegroundColor Yellow
        exit 1
    }
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not available" -ForegroundColor Red
    exit 1
}

# Build Docker image
Write-Host "`n2️⃣  Building Docker image..." -ForegroundColor Yellow
docker build -t gcr.io/crested-polygon-451704-j6/pmi-backend .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker image built successfully" -ForegroundColor Green

# Push to Google Container Registry
Write-Host "`n3️⃣  Pushing to Google Container Registry..." -ForegroundColor Yellow
docker push gcr.io/crested-polygon-451704-j6/pmi-backend

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker push failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Image pushed successfully" -ForegroundColor Green

# Deploy to Cloud Run
Write-Host "`n4️⃣  Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy pmi-backend `
    --image gcr.io/crested-polygon-451704-j6/pmi-backend `
    --platform managed `
    --region us-central1 `
    --allow-unauthenticated `
    --set-env-vars "DATABASE_URL=$env:DATABASE_URL,TWILIO_ACCOUNT_SID=$env:TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN=$env:TWILIO_AUTH_TOKEN,TWILIO_PHONE_NUMBER=$env:TWILIO_PHONE_NUMBER" `
    --timeout=600 `
    --memory=2Gi `
    --cpu=2 `
    --no-cpu-throttling `
    --max-instances=10 `
    --project crested-polygon-451704-j6

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Cloud Run deployment failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Deployed to Cloud Run successfully" -ForegroundColor Green

# Test the new endpoints
Write-Host "`n5️⃣  Testing new endpoints..." -ForegroundColor Yellow
Write-Host "Waiting 10 seconds for service to be ready..." -ForegroundColor Gray
Start-Sleep -Seconds 10

.\venv\Scripts\python.exe test_auth_booking.py

Write-Host "`n✅ Deployment complete!" -ForegroundColor Green
Write-Host "`nNew API Endpoints:" -ForegroundColor Cyan
Write-Host "  POST /api/auth/login" -ForegroundColor White
Write-Host "  GET  /api/auth/customer/{customer_id}" -ForegroundColor White
Write-Host "  POST /api/bookings/create" -ForegroundColor White
Write-Host "  GET  /api/bookings/customer/{customer_id}" -ForegroundColor White
Write-Host "`nDemo Credentials:" -ForegroundColor Cyan
Write-Host "  Email: rajesh.kumar@email.com" -ForegroundColor White
Write-Host "  Phone: +91-98765-43210" -ForegroundColor White
