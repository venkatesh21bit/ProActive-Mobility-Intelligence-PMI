"""
Quick test to verify auth and booking APIs work locally
"""
import requests
import json

BASE_URL = "https://pmi-backend-418022813675.us-central1.run.app"

print("🧪 Testing Authentication and Booking APIs\n")
print("=" * 60)

# Test 1: Login
print("\n1️⃣  Testing Login...")
print(f"POST {BASE_URL}/api/auth/login")
try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "rajesh.kumar@email.com"},
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    print(f"Status: {response.status_code}")
    if response.ok:
        login_data = response.json()
        print("✅ Login successful!")
        print(f"   Customer: {login_data['first_name']} {login_data['last_name']}")
        print(f"   Email: {login_data['email']}")
        if login_data.get('vehicle'):
            print(f"   Vehicle: {login_data['vehicle']['make']} {login_data['vehicle']['model']}")
            print(f"   VIN: {login_data['vehicle']['vin']}")
            
            customer_id = login_data['customer_id']
            vehicle_id = login_data['vehicle']['vehicle_id']
            
            # Test 2: Create Booking
            print("\n2️⃣  Testing Booking Creation...")
            print(f"POST {BASE_URL}/api/bookings/create")
            booking_response = requests.post(
                f"{BASE_URL}/api/bookings/create",
                json={
                    "customer_id": customer_id,
                    "vehicle_id": vehicle_id,
                    "service_type": "General Service",
                    "scheduled_date": "Tomorrow",
                    "scheduled_time": "10:00 AM",
                    "notes": "Regular maintenance checkup"
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            print(f"Status: {booking_response.status_code}")
            if booking_response.ok:
                booking_data = booking_response.json()
                print("✅ Booking created successfully!")
                print(f"   Appointment ID: {booking_data['appointment_id']}")
                print(f"   Service: {booking_data['service_type']}")
                print(f"   Time: {booking_data['scheduled_time']}")
                print(f"   Center: {booking_data['service_center']}")
                print(f"\n   Confirmation Message:")
                print(f"   {booking_data['confirmation_message']}")
            else:
                print(f"❌ Booking failed: {booking_response.text}")
                
    else:
        print(f"❌ Login failed: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n" + "=" * 60)
print("✅ API testing complete!")
