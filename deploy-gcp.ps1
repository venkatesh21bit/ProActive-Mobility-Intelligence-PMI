# Deployment script for GCP
# Run this after setting up GCP project

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "ProActive Mobility Intelligence" -ForegroundColor Green
Write-Host "Google Cloud Platform Deployment" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if gcloud is installed
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "Error: gcloud CLI not found!" -ForegroundColor Red
    Write-Host "Install from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Get project ID
$PROJECT_ID = Read-Host "Enter your GCP Project ID (e.g., vendor-project-12345)"
$REGION = Read-Host "Enter region (default: us-central1)" 
if ([string]::IsNullOrWhiteSpace($REGION)) {
    $REGION = "us-central1"
}

Write-Host ""
Write-Host "Using Project: $PROJECT_ID" -ForegroundColor Green
Write-Host "Region: $REGION" -ForegroundColor Green
Write-Host ""

# Set project
gcloud config set project $PROJECT_ID

Write-Host ""
Write-Host "Select deployment option:" -ForegroundColor Yellow
Write-Host "1. Deploy Backend to Cloud Run (Recommended)"
Write-Host "2. Deploy Backend to App Engine"
Write-Host "3. Setup Cloud SQL (PostgreSQL)"
Write-Host "4. Setup Redis (Memorystore)"
Write-Host "5. Deploy Frontend to Cloud Storage + CDN"
Write-Host "6. Full Setup (All services)"
Write-Host ""

$choice = Read-Host "Select option (1-6)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Deploying to Cloud Run..." -ForegroundColor Green
        
        Set-Location backend
        
        # Build container
        Write-Host "Building container..." -ForegroundColor Yellow
        gcloud builds submit --tag gcr.io/$PROJECT_ID/pmi-backend
        
        # Deploy to Cloud Run
        Write-Host "Deploying to Cloud Run..." -ForegroundColor Yellow
        gcloud run deploy pmi-backend `
            --image gcr.io/$PROJECT_ID/pmi-backend `
            --platform managed `
            --region $REGION `
            --allow-unauthenticated `
            --min-instances 1 `
            --max-instances 10 `
            --cpu 2 `
            --memory 2Gi `
            --timeout 300 `
            --port 8000
        
        Write-Host ""
        Write-Host "✓ Backend deployed to Cloud Run!" -ForegroundColor Green
        
        Set-Location ..
    }
    
    "2" {
        Write-Host ""
        Write-Host "Deploying to App Engine..." -ForegroundColor Green
        
        Set-Location backend
        
        # Deploy to App Engine
        gcloud app deploy app.yaml --project $PROJECT_ID
        
        Write-Host ""
        Write-Host "✓ Backend deployed to App Engine!" -ForegroundColor Green
        
        Set-Location ..
    }
    
    "3" {
        Write-Host ""
        Write-Host "Creating Cloud SQL PostgreSQL instance..." -ForegroundColor Green
        
        $INSTANCE_NAME = Read-Host "Enter instance name (default: pmi-postgres)"
        if ([string]::IsNullOrWhiteSpace($INSTANCE_NAME)) {
            $INSTANCE_NAME = "pmi-postgres"
        }
        
        Write-Host "Creating Cloud SQL instance (this takes 5-10 minutes)..." -ForegroundColor Yellow
        
        gcloud sql instances create $INSTANCE_NAME `
            --database-version=POSTGRES_15 `
            --tier=db-f1-micro `
            --region=$REGION `
            --network=default `
            --enable-bin-log
        
        # Create database
        Write-Host "Creating database..." -ForegroundColor Yellow
        gcloud sql databases create pmi_db --instance=$INSTANCE_NAME
        
        # Create user
        Write-Host "Creating database user..." -ForegroundColor Yellow
        $DB_PASSWORD = Read-Host "Enter database password" -AsSecureString
        $DB_PASSWORD_PLAIN = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [Runtime.InteropServices.Marshal]::SecureStringToBSTR($DB_PASSWORD)
        )
        
        gcloud sql users create pmi_user `
            --instance=$INSTANCE_NAME `
            --password=$DB_PASSWORD_PLAIN
        
        Write-Host ""
        Write-Host "✓ Cloud SQL PostgreSQL created!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Connection details:" -ForegroundColor Yellow
        Write-Host "Instance: $INSTANCE_NAME" -ForegroundColor Cyan
        Write-Host "Database: pmi_db" -ForegroundColor Cyan
        Write-Host "User: pmi_user" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Get connection string:" -ForegroundColor Yellow
        Write-Host "gcloud sql instances describe $INSTANCE_NAME --format='value(connectionName)'" -ForegroundColor Cyan
    }
    
    "4" {
        Write-Host ""
        Write-Host "Creating Redis Memorystore instance..." -ForegroundColor Green
        
        $REDIS_NAME = Read-Host "Enter Redis instance name (default: pmi-redis)"
        if ([string]::IsNullOrWhiteSpace($REDIS_NAME)) {
            $REDIS_NAME = "pmi-redis"
        }
        
        Write-Host "Creating Redis instance (this takes 5-10 minutes)..." -ForegroundColor Yellow
        
        gcloud redis instances create $REDIS_NAME `
            --size=1 `
            --region=$REGION `
            --redis-version=redis_7_0 `
            --network=default `
            --tier=basic
        
        Write-Host ""
        Write-Host "✓ Redis Memorystore created!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Get Redis connection details:" -ForegroundColor Yellow
        Write-Host "gcloud redis instances describe $REDIS_NAME --region=$REGION" -ForegroundColor Cyan
    }
    
    "5" {
        Write-Host ""
        Write-Host "Deploying Frontend to Cloud Storage + CDN..." -ForegroundColor Green
        
        Set-Location frontend
        
        # Build frontend
        Write-Host "Building frontend..." -ForegroundColor Yellow
        npm run build
        
        # Create bucket
        $BUCKET_NAME = "$PROJECT_ID-pmi-frontend"
        Write-Host "Creating Cloud Storage bucket..." -ForegroundColor Yellow
        gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME
        
        # Upload files
        Write-Host "Uploading files..." -ForegroundColor Yellow
        gsutil -m cp -r dist/* gs://$BUCKET_NAME/
        
        # Make public
        Write-Host "Configuring public access..." -ForegroundColor Yellow
        gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME
        
        # Set website config
        gsutil web set -m index.html -e index.html gs://$BUCKET_NAME
        
        Write-Host ""
        Write-Host "✓ Frontend deployed!" -ForegroundColor Green
        Write-Host "URL: https://storage.googleapis.com/$BUCKET_NAME/index.html" -ForegroundColor Cyan
        
        Set-Location ..
    }
    
    "6" {
        Write-Host ""
        Write-Host "Full GCP Setup - This will create all services" -ForegroundColor Green
        Write-Host ""
        
        # Enable APIs
        Write-Host "Enabling required APIs..." -ForegroundColor Yellow
        gcloud services enable run.googleapis.com
        gcloud services enable cloudbuild.googleapis.com
        gcloud services enable sql-component.googleapis.com
        gcloud services enable sqladmin.googleapis.com
        gcloud services enable redis.googleapis.com
        gcloud services enable compute.googleapis.com
        
        Write-Host ""
        Write-Host "APIs enabled. Now run options 1, 3, 4, and 5 individually." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
