"""
Direct asyncpg connection to Railway database for seeding
"""
import asyncio
import asyncpg
import sys
from datetime import datetime, timedelta
import random

DATABASE_URL = "postgresql://postgres:XOWvjjQCHKEIfdpUKrnnSDVFdcMmPBGA@postgres.railway.internal:5432/railway"

async def seed_direct():
    print("=" * 70)
    print("Direct Database Seeding via asyncpg")
    print("=" * 70)
    print(f"\nDatabase: {DATABASE_URL[:60]}...")
    
    try:
        # Connect to the database
        print("\n⏳ Connecting to Railway PostgreSQL...")
        conn = await asyncpg.connect(DATABASE_URL)
        print("✓ Connected!")
        
        # Check current vehicle count
        count = await conn.fetchval("SELECT COUNT(*) FROM vehicles")
        print(f"\n📊 Current vehicle count: {count}")
        
        if count > 0:
            print("⚠️  Database already has vehicles. Skipping seed.")
            await conn.close()
            return
        
        print("\n⏳ Seeding database...")
        
        # Create a customer
        print("  → Adding customer...")
        customer_id = await conn.fetchval("""
            INSERT INTO customers (first_name, last_name, email, phone, created_at)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (email) DO UPDATE SET email = EXCLUDED.email
            RETURNING id
        """, "Fleet", "Manager", "fleet@example.com", "+1234567890", datetime.utcnow())
        print(f"  ✓ Customer created (ID: {customer_id})")
        
        # Create a service center
        print("  → Adding service center...")
        center_id = await conn.fetchval("""
            INSERT INTO service_centers (name, address, city, state, zip_code, phone, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id
        """, "Main Service Center", "123 Main St", "San Francisco", "CA", "94105", "+1234567891", datetime.utcnow())
        print(f"  ✓ Service center created (ID: {center_id})")
        
        # Create vehicles
        print("  → Adding 50 vehicles...")
        hero_models = [
            ('Splendor Plus', 'Motorcycle'),
            ('HF Deluxe', 'Motorcycle'),
            ('Passion Pro', 'Motorcycle'),
            ('Glamour', 'Motorcycle'),
            ('Xtreme 160R', 'Motorcycle'),
        ]
        
        statuses = ['critical', 'warning', 'healthy']
        vehicle_ids = []
        
        for i in range(50):
            model_info = random.choice(hero_models)
            status = random.choices(statuses, weights=[0.1, 0.3, 0.6])[0]
            
            vin = f"HERO{random.randint(100000, 999999)}"
            mileage = random.randint(5000, 100000)
            year = random.randint(2018, 2024)
            
            vehicle_id = await conn.fetchval("""
                INSERT INTO vehicles (customer_id, vin, make, model, year, mileage, status, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (vin) DO NOTHING
                RETURNING id
            """, customer_id, vin, "Hero MotoCorp", model_info[0], year, mileage, status, datetime.utcnow())
            
            if vehicle_id:
                vehicle_ids.append(vehicle_id)
        
        print(f"  ✓ Created {len(vehicle_ids)} vehicles")
        
        # Create telemetry for each vehicle
        print("  → Adding telemetry data...")
        for vehicle_id in vehicle_ids:
            await conn.execute("""
                INSERT INTO vehicle_telemetry (
                    vehicle_id, speed, rpm, fuel_level, engine_temp,
                    oil_pressure, battery_voltage, tire_pressure_fl,
                    tire_pressure_fr, tire_pressure_rl, tire_pressure_rr,
                    latitude, longitude, timestamp
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            """, vehicle_id, random.uniform(0, 80), random.uniform(800, 5000),
                random.uniform(10, 100), random.uniform(70, 110),
                random.uniform(20, 60), random.uniform(12, 14),
                random.uniform(28, 35), random.uniform(28, 35),
                random.uniform(28, 35), random.uniform(28, 35),
                37.7749 + random.uniform(-0.5, 0.5),
                -122.4194 + random.uniform(-0.5, 0.5),
                datetime.utcnow())
        
        print(f"  ✓ Added telemetry for {len(vehicle_ids)} vehicles")
        
        # Final counts
        vehicle_count = await conn.fetchval("SELECT COUNT(*) FROM vehicles")
        customer_count = await conn.fetchval("SELECT COUNT(*) FROM customers")
        telemetry_count = await conn.fetchval("SELECT COUNT(*) FROM vehicle_telemetry")
        
        print("\n" + "=" * 70)
        print("✅ Database Seeding Complete!")
        print("=" * 70)
        print(f"  📊 Customers: {customer_count}")
        print(f"  🚗 Vehicles: {vehicle_count}")
        print(f"  📡 Telemetry Records: {telemetry_count}")
        print("=" * 70)
        
        await conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(seed_direct())
