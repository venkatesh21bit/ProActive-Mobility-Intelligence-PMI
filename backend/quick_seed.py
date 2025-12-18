import asyncio
import asyncpg

async def seed_demo_customer():
    # Connect to Cloud SQL
    conn = await asyncpg.connect(
        user='postgres',
        password='auto1234',
        host='34.16.54.105',
        database='automotive_db'
    )
    
    try:
        # Insert customer
        customer_id = await conn.fetchval('''
            INSERT INTO customers (first_name, last_name, email, phone, address, city, state, zip_code, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
            ON CONFLICT (email) DO UPDATE SET 
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                phone = EXCLUDED.phone,
                address = EXCLUDED.address,
                city = EXCLUDED.city,
                state = EXCLUDED.state,
                zip_code = EXCLUDED.zip_code,
                updated_at = NOW()
            RETURNING customer_id
        ''', 'Rajesh', 'Kumar', 'rajesh.kumar@email.com', '+91-9876543210', '123 MG Road', 'Mumbai', 'Maharashtra', '400001')
        
        print(f"✅ Customer created/updated: ID = {customer_id}")
        
        # Insert vehicle
        vehicle_id = await conn.fetchval('''
            INSERT INTO vehicles (vin, customer_id, make, model, year, license_plate, odometer, fuel_type, transmission_type, engine_type, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW(), NOW())
            ON CONFLICT (vin) DO UPDATE SET
                odometer = EXCLUDED.odometer,
                updated_at = NOW()
            RETURNING vehicle_id
        ''', 'HERO735950001', customer_id, 'Hero MotoCorp', 'Super Splendor', 2023, 'MH01AB1234', 5000, 'Petrol', 'Manual', '4-Stroke Single Cylinder')
        
        print(f"✅ Vehicle created/updated: ID = {vehicle_id}, VIN = HERO735950001")
        print(f"\n✅ Demo customer ready!")
        print(f"   Email: rajesh.kumar@email.com")
        print(f"   Vehicle: 2023 Hero MotoCorp Super Splendor")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(seed_demo_customer())
