# Deploy Backend with Twilio Integration

Write-Host "Deploying PMI Backend with Twilio Integration..." -ForegroundColor Cyan

# Set project variables
$PROJECT_ID = "crested-polygon-451704-j6"
$REGION = "us-central1"
$SERVICE_NAME = "pmi-backend"

# Twilio credentials - Set these as environment variables before running
if (-not $env:TWILIO_ACCOUNT_SID) {
    Write-Host "❌ Error: TWILIO_ACCOUNT_SID environment variable not set" -ForegroundColor Red
    Write-Host "Set it with: `$env:TWILIO_ACCOUNT_SID = 'your_account_sid'" -ForegroundColor Yellow
    exit 1
}
if (-not $env:TWILIO_AUTH_TOKEN) {
    Write-Host "❌ Error: TWILIO_AUTH_TOKEN environment variable not set" -ForegroundColor Red
    Write-Host "Set it with: `$env:TWILIO_AUTH_TOKEN = 'your_auth_token'" -ForegroundColor Yellow
    exit 1
}
if (-not $env:TWILIO_PHONE_NUMBER) {
    Write-Host "❌ Error: TWILIO_PHONE_NUMBER environment variable not set" -ForegroundColor Red
    Write-Host "Set it with: `$env:TWILIO_PHONE_NUMBER = 'your_phone_number'" -ForegroundColor Yellow
    exit 1
}

$TWILIO_ACCOUNT_SID = $env:TWILIO_ACCOUNT_SID
$TWILIO_AUTH_TOKEN = $env:TWILIO_AUTH_TOKEN
$TWILIO_PHONE_NUMBER = $env:TWILIO_PHONE_NUMBER

# Build Docker image
Write-Host ""
Write-Host "Building Docker image..." -ForegroundColor Yellow
Set-Location backend
gcloud builds submit --tag gcr.io/$PROJECT_ID/${SERVICE_NAME}:latest

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}

# Deploy to Cloud Run with all environment variables
Write-Host ""
Write-Host "Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $SERVICE_NAME `
    --image gcr.io/$PROJECT_ID/${SERVICE_NAME}:latest `
    --region $REGION `
    --platform managed `
    --allow-unauthenticated `
    --set-env-vars "TWILIO_ACCOUNT_SID=$TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN=$TWILIO_AUTH_TOKEN,TWILIO_PHONE_NUMBER=$TWILIO_PHONE_NUMBER,DATABASE_URL=postgresql://pmi_user:pmi_password_2024@34.122.2.67:5432/pmi_db,REDIS_URL=redis://34.170.219.189:6379,CORS_ORIGINS=*"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Deployment failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Backend deployed successfully with Twilio integration!" -ForegroundColor Green
Write-Host ""
Write-Host "Twilio Configuration:" -ForegroundColor Cyan
Write-Host "  Account SID: $TWILIO_ACCOUNT_SID"
Write-Host "  Phone Number: $TWILIO_PHONE_NUMBER"
Write-Host ""
Write-Host "Service URL: https://pmi-backend-418022813675.us-central1.run.app" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test SMS Alert:" -ForegroundColor Yellow
Write-Host '  curl -X POST https://pmi-backend-418022813675.us-central1.run.app/api/notifications/send-alert \'
Write-Host '    -H "Content-Type: application/json" \'
Write-Host '    -d "{\"customer_id\": 1, \"vehicle_id\": 2, \"prediction_id\": 30, \"channel\": \"sms\"}"'
