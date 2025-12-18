-- Insert demo customer
INSERT INTO customers (first_name, last_name, email, phone, address, city, state, zip_code, created_at)
VALUES ('Rajesh', 'Kumar', 'rajesh.kumar@email.com', '+91-9876543210', '123 MG Road', 'Mumbai', 'Maharashtra', '400001', NOW())
ON CONFLICT (email) DO NOTHING;

-- Get the customer_id (assuming it's 1 or the first one)
-- Insert demo vehicle
INSERT INTO vehicles (vin, customer_id, make, model, year, license_plate, odometer, fuel_type, transmission_type, engine_type, created_at)
SELECT 'HERO735950001', customer_id, 'Hero', 'Super Splendor', 2023, 'MH01AB1234', 5000, 'Petrol', 'Manual', '4-Stroke', NOW()
FROM customers WHERE email = 'rajesh.kumar@email.com'
ON CONFLICT (vin) DO NOTHING;
