# 🔐 Setting Up Twilio Credentials

## For Local Development

1. Get your Twilio credentials from: https://console.twilio.com/

2. Create a `.env` file in the `backend` directory:
```bash
cd backend
cp .env.example .env
```

3. Edit `.env` and add your credentials:
```bash
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=your_twilio_phone_number
```

## For Cloud Deployment

### Set Environment Variables in PowerShell:
```powershell
$env:TWILIO_ACCOUNT_SID = "your_account_sid_here"
$env:TWILIO_AUTH_TOKEN = "your_auth_token_here"
$env:TWILIO_PHONE_NUMBER = "your_twilio_phone_number"
```

### Then run the deployment script:
```powershell
.\deploy-backend.ps1
```

The script will automatically use your environment variables.

## Where to Find Your Credentials

1. **Account SID**: Found on your Twilio Console Dashboard
2. **Auth Token**: Click "Show" next to Auth Token on the Dashboard
3. **Phone Number**: Go to Phone Numbers → Manage → Active numbers

## Security Note

⚠️ **NEVER commit your actual credentials to Git!**
- Use `.env` files for local development (already in `.gitignore`)
- Use environment variables for deployment
- Use secrets management for production
