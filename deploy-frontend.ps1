# Deploy Frontend to Firebase

Write-Host "Deploying PMI Frontend..." -ForegroundColor Cyan

Set-Location frontend

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Build production bundle
Write-Host "Building production bundle..." -ForegroundColor Yellow
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

# Deploy to Firebase
Write-Host "Deploying to Firebase Hosting..." -ForegroundColor Yellow
firebase deploy --only hosting

if ($LASTEXITCODE -ne 0) {
    Write-Host "Deployment failed!" -ForegroundColor Red
    exit 1
}

Write-Host "Frontend deployed successfully!" -ForegroundColor Green
Write-Host "Live URL: https://pmi-1234.web.app" -ForegroundColor Cyan
Write-Host ""
Write-Host "Features Available:" -ForegroundColor Yellow
Write-Host "  - Multi-page dashboard with routing"
Write-Host "  - Notification Center with Twilio SMS/Voice"
Write-Host "  - Dashboard with real-time stats"
Write-Host "  - Vehicles, Alerts, Appointments (placeholder)"
Write-Host "  - Analytics charts (coming soon)"
Write-Host "  - Settings panel (coming soon)"
