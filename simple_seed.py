"""
Direct database seeding using psycopg2 (synchronous)
This can be run via: railway run python simple_seed.py
"""
import os
import sys

# Database URL from Railway
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:XOWvjjQCHKEIfdpUKrnnSDVFdcMmPBGA@postgres.railway.internal:5432/railway")

print("=" * 70)
print("Simple Database Seeding Script")
print("=" * 70)
print(f"\nDatabase: {DATABASE_URL[:60]}...")

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    print("✓ psycopg2 imported")
except ImportError:
    print("❌ psycopg2 not installed. Installing...")
    os.system("pip install psycopg2-binary")
    import psycopg2
    from psycopg2.extras import RealDictCursor

# Connect to database
print("\n⏳ Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor(cursor_factory=RealDictCursor)
print("✓ Connected!")

# Check if tables exist
print("\n⏳ Checking tables...")
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name;
""")
tables = cur.fetchall()
print(f"✓ Found {len(tables)} tables: {', '.join([t['table_name'] for t in tables])}")

# Check if data already exists
cur.execute("SELECT COUNT(*) as count FROM vehicles")
vehicle_count = cur.fetchone()['count']
print(f"\n📊 Current vehicle count: {vehicle_count}")

if vehicle_count > 0:
    print("\n⚠️  Database already has vehicles. Skipping seed.")
    cur.close()
    conn.close()
    sys.exit(0)

print("\n⏳ Seeding database...")

# Seed Customers
print("  → Adding customers...")
customers_data = [
    ("John Doe", "john.doe@email.com", "+1234567890"),
    ("Jane Smith", "jane.smith@email.com", "+1234567891"),
    ("Bob Johnson", "bob.j@email.com", "+1234567892"),
]

for name, email, phone in customers_data:
    cur.execute("""
        INSERT INTO customers (name, email, phone)
        VALUES (%s, %s, %s)
        ON CONFLICT (email) DO NOTHING
    """, (name, email, phone))

conn.commit()
print(f"  ✓ Added {len(customers_data)} customers")

# Get customer IDs
cur.execute("SELECT id FROM customers LIMIT 3")
customer_ids = [row['id'] for row in cur.fetchall()]

# Seed Vehicles
print("  → Adding vehicles...")
vehicles_data = [
    (customer_ids[0] if customer_ids else 1, "ABC123", "Toyota", "Camry", 2020, 15000),
    (customer_ids[1] if len(customer_ids) > 1 else 1, "XYZ789", "Honda", "Civic", 2019, 25000),
    (customer_ids[2] if len(customer_ids) > 2 else 1, "DEF456", "Ford", "F-150", 2021, 12000),
]

for customer_id, vin, make, model, year, mileage in vehicles_data:
    cur.execute("""
        INSERT INTO vehicles (customer_id, vin, make, model, year, mileage)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (vin) DO NOTHING
    """, (customer_id, vin, make, model, year, mileage))

conn.commit()
print(f"  ✓ Added {len(vehicles_data)} vehicles")

# Get vehicle IDs
cur.execute("SELECT id FROM vehicles LIMIT 3")
vehicle_ids = [row['id'] for row in cur.fetchall()]

# Seed Vehicle Health
print("  → Adding vehicle health data...")
for vehicle_id in vehicle_ids:
    cur.execute("""
        INSERT INTO vehicle_health (vehicle_id, overall_health, engine_status, transmission_status, brake_status, battery_voltage, tire_pressure)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (vehicle_id) DO UPDATE SET
            overall_health = EXCLUDED.overall_health,
            last_updated = CURRENT_TIMESTAMP
    """, (vehicle_id, 85.5, "good", "good", "good", 12.5, 32.0))

conn.commit()
print(f"  ✓ Added health data for {len(vehicle_ids)} vehicles")

# Seed Maintenance Records
print("  → Adding maintenance records...")
for vehicle_id in vehicle_ids:
    cur.execute("""
        INSERT INTO maintenance_records (vehicle_id, service_type, service_date, cost, notes)
        VALUES (%s, %s, CURRENT_DATE - INTERVAL '30 days', %s, %s)
    """, (vehicle_id, "Oil Change", 50.00, "Regular maintenance"))

conn.commit()
print(f"  ✓ Added maintenance records")

# Final counts
cur.execute("SELECT COUNT(*) as count FROM customers")
customer_count = cur.fetchone()['count']

cur.execute("SELECT COUNT(*) as count FROM vehicles")
vehicle_count = cur.fetchone()['count']

cur.execute("SELECT COUNT(*) as count FROM vehicle_health")
health_count = cur.fetchone()['count']

cur.execute("SELECT COUNT(*) as count FROM maintenance_records")
maintenance_count = cur.fetchone()['count']

print("\n" + "=" * 70)
print("✅ Database Seeding Complete!")
print("=" * 70)
print(f"  📊 Customers: {customer_count}")
print(f"  🚗 Vehicles: {vehicle_count}")
print(f"  ❤️  Health Records: {health_count}")
print(f"  🔧 Maintenance Records: {maintenance_count}")
print("=" * 70)

cur.close()
conn.close()
