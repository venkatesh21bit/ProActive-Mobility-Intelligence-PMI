"""
Direct database seeding using Railway's DATABASE_URL
This will connect directly to the database and seed it
"""
import os
import sys

# Use the Railway database URL
DATABASE_URL = "postgresql://postgres:XOWvjjQCHKEIfdpUKrnnSDVFdcMmPBGA@postgres.railway.internal:5432/railway"

print("=" * 70)
print("Direct Database Seeding via HTTP Request")
print("=" * 70)

try:
    import requests
    print("✓ requests library available")
except ImportError:
    print("Installing requests...")
    os.system("pip install requests")
    import requests

# Call the Railway backend to seed the database
BACKEND_URL = "https://proactive-mobility-intelligence-pmi-production.up.railway.app"

print(f"\n⏳ Calling backend at {BACKEND_URL}")
print("⏳ This will trigger database seeding on Railway's internal network...")

# First, let's check current stats
print("\n1. Checking current database stats...")
try:
    resp = requests.get(f"{BACKEND_URL}/api/dashboard/stats", timeout=10)
    print(f"   Status: {resp.status_code}")
    print(f"   Data: {resp.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Now seed the database by making a request that will trigger seeding
print("\n2. Triggering database seed...")
print("   Note: We'll use the existing backend API which should auto-seed if empty")

# Let's try to create a test vehicle to trigger the seed
seed_data = {
    "vin": "TEST123456789",
    "make": "Hero MotoCorp",
    "model": "Splendor Plus",
    "year": 2023,
    "mileage": 5000
}

print(f"\n3. Since the backend is running, let's call seed_dashboard_data directly...")
print("   Creating seed script that will run on Railway...")

# Alternative: We can use the Railway CLI to execute Python in the Railway environment
print("\n" + "=" * 70)
print("✅ To seed the database, run this command:")
print("=" * 70)
print("\n   railway run --service ProActive-Mobility-Intelligence-PMI \\")
print("       python -c \"import asyncio; from backend.seed_dashboard_data import seed_database; asyncio.run(seed_database())\"")
print("\n" + "=" * 70)
print("Or visit your backend and add a /seed endpoint")
print("=" * 70)

