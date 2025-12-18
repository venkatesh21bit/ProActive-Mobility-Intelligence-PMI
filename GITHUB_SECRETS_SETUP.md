# GitHub Secrets Setup Guide

To enable automated deployments via GitHub Actions, you need to configure the following secrets in your repository.

## How to Add Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret below

## Required Secrets

### Google Cloud Platform

#### `GCP_SA_KEY`
- **Description**: Service account JSON key for GCP authentication
- **How to get**:
  1. Go to [GCP Console](https://console.cloud.google.com/)
  2. Navigate to **IAM & Admin** → **Service Accounts**
  3. Create or select a service account
  4. Click **Keys** → **Add Key** → **Create new key** → **JSON**
  5. Copy the entire JSON file content
  6. Paste as secret value

#### `GCP_PROJECT_ID`
- **Value**: `crested-polygon-451704-j6`
- **Description**: Your GCP project ID

### Database

#### `DATABASE_URL`
- **Value**: `postgresql://pmi_user:pmi_password_2024@34.122.2.67:5432/pmi_db`
- **Description**: PostgreSQL connection string

#### `REDIS_URL`
- **Value**: `redis://34.170.219.189:6379`
- **Description**: Redis connection string

### Twilio (SMS & Voice)

#### `TWILIO_ACCOUNT_SID`
- **Value**: Your Twilio Account SID
- **Where to find**: [Twilio Console Dashboard](https://console.twilio.com/)

#### `TWILIO_AUTH_TOKEN`
- **Value**: Your Twilio Auth Token
- **Where to find**: [Twilio Console Dashboard](https://console.twilio.com/) (click "Show")

#### `TWILIO_PHONE_NUMBER`
- **Value**: Your Twilio phone number (format: +1234567890)
- **Where to find**: [Twilio Phone Numbers](https://console.twilio.com/phone-numbers)

### Application Configuration

#### `CORS_ORIGINS`
- **Value**: `*` (for development) or specific domains (for production)
- **Example**: `https://pmi-1234.web.app,https://yourdomain.com`

#### `VITE_API_URL`
- **Value**: `https://pmi-backend-418022813675.us-central1.run.app`
- **Description**: Backend API URL for frontend

## Optional: Disable GCP Deployment

If you don't have GCP secrets configured yet, the workflow will skip the deployment job automatically. The tests will still run.

## Verify Setup

After adding secrets, push to master branch:
```bash
git add .
git commit -m "Update workflow configuration"
git push origin master
```

Check the **Actions** tab to see the workflow run.
