-- Create demo customer Rajesh Kumar
INSERT INTO customers (first_name, last_name, email, phone, address, city, state, zip_code, created_at, updated_at)
VALUES ('Rajesh', 'Kumar', 'rajesh.kumar@email.com', '+91-9876543210', '123 MG Road', 'Mumbai', 'Maharashtra', '400001', NOW(), NOW())
ON CONFLICT (email) DO UPDATE SET 
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    phone = EXCLUDED.phone,
    address = EXCLUDED.address,
    city = EXCLUDED.city,
    state = EXCLUDED.state,
    zip_code = EXCLUDED.zip_code,
    updated_at = NOW()
RETURNING customer_id;

-- Create demo vehicle for Rajesh
INSERT INTO vehicles (vin, customer_id, make, model, year, license_plate, odometer, fuel_type, transmission_type, engine_type, created_at, updated_at)
SELECT 'HERO735950001', customer_id, 'Hero MotoCorp', 'Super Splendor', 2023, 'MH01AB1234', 5000, 'Petrol', 'Manual', '4-Stroke Single Cylinder', NOW(), NOW()
FROM customers WHERE email = 'rajesh.kumar@email.com'
ON CONFLICT (vin) DO UPDATE SET
    odometer = EXCLUDED.odometer,
    updated_at = NOW()
RETURNING vehicle_id, vin, make, model;
