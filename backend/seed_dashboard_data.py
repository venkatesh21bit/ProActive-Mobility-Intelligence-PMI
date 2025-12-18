"""
Seed database with sample data for testing the dashboard
"""
import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy import select
from data.database import AsyncSessionLocal
from data.models import Vehicle, VehicleTelemetry, FailurePrediction, Appointment, Customer, ServiceCenter

async def seed_database():
    async with AsyncSessionLocal() as db:
        # Check if data already exists
        result = await db.execute(select(Vehicle).limit(1))
        if result.scalar_one_or_none():
            print("Database already has data. Skipping seed.")
            return
        
        print("Seeding database with sample data...")
        
        # Create a customer
        customer = Customer(
            first_name="Fleet",
            last_name="Manager",
            email="fleet@example.com",
            phone="+1234567890"
        )
        db.add(customer)
        
        # Create a service center
        service_center = ServiceCenter(
            name="Main Service Center",
            address="123 Main St",
            city="San Francisco",
            state="CA",
            zip_code="94105",
            phone="+1234567891"
        )
        db.add(service_center)
        
        # Create 50 vehicles with varying health states - Hero MotoCorp models
        vehicles = []
        statuses = ['critical', 'warning', 'healthy']
        probabilities = [0.1, 0.3, 0.6]  # 10% critical, 30% warning, 60% healthy
        
        hero_models = [
            ('Splendor Plus', 'Motorcycle'),
            ('HF Deluxe', 'Motorcycle'),
            ('Passion Pro', 'Motorcycle'),
            ('Glamour', 'Motorcycle'),
            ('Super Splendor', 'Motorcycle'),
            ('Xtreme 160R', 'Motorcycle'),
            ('Xpulse 200', 'Adventure'),
            ('Maestro Edge', 'Scooter'),
            ('Pleasure Plus', 'Scooter'),
            ('Destini 125', 'Scooter')
        ]
        
        # Flush to get customer_id
        await db.flush()
        
        for i in range(1, 51):
            status = random.choices(statuses, probabilities)[0]
            model, category = random.choice(hero_models)
            
            vehicle = Vehicle(
                vin=f"HERO{random.randint(100000, 999999)}{i:03d}",
                customer_id=customer.customer_id,
                make="Hero MotoCorp",
                model=model,
                year=2020 + (i % 5),
                purchase_date=datetime.now() - timedelta(days=random.randint(365, 1825))
            )
            vehicles.append(vehicle)
            db.add(vehicle)
            await db.flush()  # Get vehicle_id
            
            # Create telemetry for each vehicle
            telemetry = VehicleTelemetry(
                time=datetime.now() - timedelta(minutes=random.randint(1, 60)),
                vehicle_id=vehicle.vin,  # Telemetry uses VIN as vehicle_id
                vin=vehicle.vin,
                engine_temperature=90 + random.uniform(-10, 20) if status != 'critical' else 110 + random.uniform(0, 15),
                coolant_temperature=85 + random.uniform(-5, 10),
                oil_pressure=45 + random.uniform(-5, 5) if status != 'critical' else 25 + random.uniform(-5, 5),
                vibration_level=0.5 + random.uniform(0, 0.3) if status != 'critical' else 1.2 + random.uniform(0, 0.5),
                rpm=2000 + random.uniform(-500, 1000),
                speed=60 + random.uniform(-20, 20),
                fuel_level=50 + random.uniform(-30, 40),
                battery_voltage=12.6 + random.uniform(-0.3, 0.3),
                odometer=50000 + random.randint(0, 100000)
            )
            db.add(telemetry)
            
            # Create predictions
            if status == 'critical':
                failure_prob = 0.75 + random.uniform(0, 0.20)
                component = random.choice(['engine', 'transmission', 'brakes', 'oil_system'])
            elif status == 'warning':
                failure_prob = 0.55 + random.uniform(0, 0.15)
                component = random.choice(['battery', 'cooling_system', 'suspension'])
            else:
                failure_prob = 0.15 + random.uniform(0, 0.25)
                component = random.choice(['tires', 'filters', 'fluids'])
            
            prediction = FailurePrediction(
                vehicle_id=vehicle.vehicle_id,
                vin=vehicle.vin,
                prediction_time=datetime.now() - timedelta(hours=random.randint(1, 24)),
                failure_probability=min(failure_prob, 0.99),
                predicted_component=component,
                severity=status,
                confidence_score=0.85 + random.uniform(0, 0.10),
                estimated_days_to_failure=7 if status == 'critical' else (30 if status == 'warning' else 90)
            )
            db.add(prediction)
            
            # Create appointments for critical and some warning vehicles
            if status == 'critical' or (status == 'warning' and random.random() < 0.5):
                appointment = Appointment(
                    vehicle_id=vehicle.vehicle_id,
                    customer_id=customer.customer_id,
                    center_id=service_center.center_id,
                    scheduled_time=datetime.now() + timedelta(days=random.randint(1, 14)),
                    appointment_type="Preventive Maintenance" if status == 'warning' else "Emergency Repair",
                    estimated_duration_minutes=120 if status == 'warning' else 240,
                    status="scheduled" if random.random() < 0.7 else "confirmed"
                )
                db.add(appointment)
        
        await db.commit()
        print(f"✅ Successfully seeded database with:")
        print(f"   - 1 customer")
        print(f"   - 1 service center")
        print(f"   - 50 vehicles")
        print(f"   - 50 telemetry records")
        print(f"   - 50 predictions")
        print(f"   - ~25 appointments")
        

if __name__ == "__main__":
    asyncio.run(seed_database())
