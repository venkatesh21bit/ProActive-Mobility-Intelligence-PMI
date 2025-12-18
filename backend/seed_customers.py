"""
Seed realistic customer and service center data
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select, update
from data.database import AsyncSessionLocal
from data.models import Customer, Vehicle, ServiceCenter


async def seed_customers_and_centers():
    """Seed realistic customer data and service centers"""
    
    async with AsyncSessionLocal() as session:
        try:
            # Check if customers already exist
            result = await session.execute(select(Customer))
            existing_customers = result.scalars().all()
            
            if len(existing_customers) > 0:
                print(f"✅ Found {len(existing_customers)} existing customers")
                
                # Update first customer for demo login
                first_customer = existing_customers[0]
                first_customer.first_name = "Rajesh"
                first_customer.last_name = "Kumar"
                first_customer.email = "rajesh.kumar@email.com"
                first_customer.phone = "+91-98765-43210"
                first_customer.address = "Flat 302, Green Heights, Andheri West, Mumbai, Maharashtra 400058"
                
                print(f"\n✅ Updated demo customer:")
                print(f"   Name: {first_customer.first_name} {first_customer.last_name}")
                print(f"   Email: {first_customer.email}")
                print(f"   Phone: {first_customer.phone}")
                
                # Get their vehicle with VIN HERO2020A000000
                vehicle_result = await session.execute(
                    select(Vehicle).where(
                        Vehicle.customer_id == first_customer.customer_id,
                        Vehicle.vin == 'HERO2020A000000'
                    )
                )
                vehicle = vehicle_result.scalar_one_or_none()
                
                if vehicle:
                    print(f"\n✅ Customer's vehicle:")
                    print(f"   {vehicle.make} {vehicle.model} ({vehicle.year})")
                    print(f"   VIN: {vehicle.vin}")
                    print(f"   Mileage: {vehicle.mileage} km")
                else:
                    # Get their first vehicle if the specific VIN doesn't exist
                    vehicle_result = await session.execute(
                        select(Vehicle).where(Vehicle.customer_id == first_customer.customer_id).limit(1)
                    )
                    vehicle = vehicle_result.scalar_one_or_none()
                    if vehicle:
                        print(f"\n✅ Customer's vehicle:")
                        print(f"   {vehicle.make} {vehicle.model} ({vehicle.year})")
                        print(f"   VIN: {vehicle.vin}")
                        print(f"   Mileage: {vehicle.mileage} km")
                
            else:
                # Create new customers
                customers_data = [
                    {
                        "first_name": "Rajesh",
                        "last_name": "Kumar",
                        "email": "rajesh.kumar@email.com",
                        "phone": "+91-98765-43210",
                        "address": "Flat 302, Green Heights, Andheri West, Mumbai, Maharashtra 400058"
                    },
                    {
                        "first_name": "Priya",
                        "last_name": "Sharma",
                        "email": "priya.sharma@email.com",
                        "phone": "+91-98765-43211",
                        "address": "House No. 45, Sector 21, Noida, Uttar Pradesh 201301"
                    },
                    {
                        "first_name": "Amit",
                        "last_name": "Patel",
                        "email": "amit.patel@email.com",
                        "phone": "+91-98765-43212",
                        "address": "Bungalow 12, Satellite Road, Ahmedabad, Gujarat 380015"
                    },
                    {
                        "first_name": "Sneha",
                        "last_name": "Reddy",
                        "email": "sneha.reddy@email.com",
                        "phone": "+91-98765-43213",
                        "address": "Apartment 204, Jubilee Hills, Hyderabad, Telangana 500033"
                    },
                    {
                        "first_name": "Vikram",
                        "last_name": "Singh",
                        "email": "vikram.singh@email.com",
                        "phone": "+91-98765-43214",
                        "address": "Villa 8, DLF Phase 4, Gurgaon, Haryana 122002"
                    }
                ]
                
                for customer_data in customers_data:
                    customer = Customer(**customer_data)
                    session.add(customer)
                
                print(f"✅ Created {len(customers_data)} new customers")
            
            # Create/Update Service Centers
            center_result = await session.execute(select(ServiceCenter))
            existing_centers = center_result.scalars().all()
            
            if len(existing_centers) > 0:
                print(f"\n✅ Found {len(existing_centers)} existing service centers")
            else:
                service_centers = [
                    {
                        "name": "Hero MotoCorp Service Center - Andheri",
                        "address": "Plot No. 45, Link Road, Andheri West",
                        "city": "Mumbai",
                        "state": "Maharashtra",
                        "zip_code": "400053",
                        "phone": "+91-22-2673-4500",
                        "email": "andheri@heromotocorp.com",
                        "capacity": 25,
                        "latitude": 19.1358,
                        "longitude": 72.8261
                    },
                    {
                        "name": "Hero MotoCorp Service Center - Bandra",
                        "address": "Shop 12, Hill Road, Bandra West",
                        "city": "Mumbai",
                        "state": "Maharashtra",
                        "zip_code": "400050",
                        "phone": "+91-22-2640-3200",
                        "email": "bandra@heromotocorp.com",
                        "capacity": 20,
                        "latitude": 19.0596,
                        "longitude": 72.8295
                    },
                    {
                        "name": "Hero MotoCorp Service Center - Thane",
                        "address": "Eastern Express Highway, Thane",
                        "city": "Thane",
                        "state": "Maharashtra",
                        "zip_code": "400601",
                        "phone": "+91-22-2534-7800",
                        "email": "thane@heromotocorp.com",
                        "capacity": 30,
                        "latitude": 19.2183,
                        "longitude": 72.9781
                    }
                ]
                
                for center_data in service_centers:
                    center = ServiceCenter(**center_data)
                    session.add(center)
                
                print(f"✅ Created {len(service_centers)} service centers")
            
            await session.commit()
            print("\n🎉 Database seeded successfully!")
            print("\n" + "="*60)
            print("LOGIN CREDENTIALS FOR MOBILE APP:")
            print("="*60)
            print("Email: rajesh.kumar@email.com")
            print("Phone: +91-98765-43210")
            print("="*60)
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding data: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_customers_and_centers())
