-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Create telemetry table for time-series data
CREATE TABLE IF NOT EXISTS vehicle_telemetry (
    time TIMESTAMPTZ NOT NULL,
    vehicle_id VARCHAR(50) NOT NULL,
    vin VARCHAR(17) NOT NULL,
    engine_temperature FLOAT,
    coolant_temperature FLOAT,
    oil_pressure FLOAT,
    vibration_level FLOAT,
    rpm INTEGER,
    speed FLOAT,
    fuel_level FLOAT,
    battery_voltage FLOAT,
    odometer INTEGER,
    latitude FLOAT,
    longitude FLOAT,
    metadata JSONB
);

-- Convert to hypertable (TimescaleDB)
SELECT create_hypertable('vehicle_telemetry', 'time', if_not_exists => TRUE);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_vehicle_telemetry_vehicle_id_time ON vehicle_telemetry (vehicle_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_vehicle_telemetry_vin ON vehicle_telemetry (vin);
CREATE INDEX IF NOT EXISTS idx_vehicle_telemetry_metadata ON vehicle_telemetry USING GIN (metadata);

-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create vehicles table
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id SERIAL PRIMARY KEY,
    vin VARCHAR(17) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(customer_id),
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year INTEGER NOT NULL,
    mileage INTEGER DEFAULT 0,
    purchase_date DATE,
    warranty_expiry DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create service centers table
CREATE TABLE IF NOT EXISTS service_centers (
    center_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    phone VARCHAR(20),
    email VARCHAR(255),
    capacity INTEGER DEFAULT 10,
    latitude FLOAT,
    longitude FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create appointments table
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id SERIAL PRIMARY KEY,
    vehicle_id INTEGER REFERENCES vehicles(vehicle_id),
    customer_id INTEGER REFERENCES customers(customer_id),
    center_id INTEGER REFERENCES service_centers(center_id),
    scheduled_time TIMESTAMPTZ NOT NULL,
    appointment_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'scheduled',
    predicted_issue TEXT,
    actual_issue TEXT,
    estimated_duration_minutes INTEGER,
    actual_duration_minutes INTEGER,
    cost DECIMAL(10, 2),
    customer_consent BOOLEAN DEFAULT FALSE,
    consent_timestamp TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_appointments_vehicle_id ON appointments (vehicle_id);
CREATE INDEX IF NOT EXISTS idx_appointments_scheduled_time ON appointments (scheduled_time);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments (status);

-- Create RCA/CAPA (Root Cause Analysis / Corrective and Preventive Action) table
CREATE TABLE IF NOT EXISTS rca_capa_records (
    record_id SERIAL PRIMARY KEY,
    incident_date TIMESTAMPTZ NOT NULL,
    vehicle_id INTEGER REFERENCES vehicles(vehicle_id),
    vin VARCHAR(17),
    component_name VARCHAR(255) NOT NULL,
    failure_mode VARCHAR(255) NOT NULL,
    root_cause TEXT NOT NULL,
    corrective_action TEXT,
    preventive_action TEXT,
    severity VARCHAR(50),
    occurrence_count INTEGER DEFAULT 1,
    design_change_required BOOLEAN DEFAULT FALSE,
    manufacturing_process_change BOOLEAN DEFAULT FALSE,
    supplier VARCHAR(255),
    part_number VARCHAR(100),
    embedding_vector VECTOR(384),  -- For semantic similarity search
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rca_capa_component ON rca_capa_records (component_name);
CREATE INDEX IF NOT EXISTS idx_rca_capa_failure_mode ON rca_capa_records (failure_mode);
CREATE INDEX IF NOT EXISTS idx_rca_capa_vehicle ON rca_capa_records (vehicle_id);

-- Create maintenance records table
CREATE TABLE IF NOT EXISTS maintenance_records (
    maintenance_id SERIAL PRIMARY KEY,
    appointment_id INTEGER REFERENCES appointments(appointment_id),
    vehicle_id INTEGER REFERENCES vehicles(vehicle_id),
    service_date TIMESTAMPTZ NOT NULL,
    service_type VARCHAR(100) NOT NULL,
    components_replaced TEXT[],
    labor_hours DECIMAL(5, 2),
    parts_cost DECIMAL(10, 2),
    labor_cost DECIMAL(10, 2),
    total_cost DECIMAL(10, 2),
    technician_notes TEXT,
    customer_feedback TEXT,
    feedback_rating INTEGER CHECK (feedback_rating >= 1 AND feedback_rating <= 5),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_maintenance_vehicle ON maintenance_records (vehicle_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_service_date ON maintenance_records (service_date);

-- Create predictions table for ML model outputs
CREATE TABLE IF NOT EXISTS failure_predictions (
    prediction_id SERIAL PRIMARY KEY,
    vehicle_id INTEGER REFERENCES vehicles(vehicle_id),
    vin VARCHAR(17) NOT NULL,
    prediction_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    predicted_component VARCHAR(255) NOT NULL,
    failure_probability FLOAT NOT NULL,
    severity VARCHAR(50) NOT NULL,
    estimated_days_to_failure INTEGER,
    confidence_score FLOAT,
    model_version VARCHAR(50),
    feature_importance JSONB,
    explanation TEXT,
    action_taken VARCHAR(100),
    actual_failure BOOLEAN,
    actual_failure_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Convert predictions to hypertable for efficient time-series queries
SELECT create_hypertable('failure_predictions', 'prediction_time', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_predictions_vehicle ON failure_predictions (vehicle_id);
CREATE INDEX IF NOT EXISTS idx_predictions_severity ON failure_predictions (severity);

-- Create agent audit log for UEBA
CREATE TABLE IF NOT EXISTS agent_audit_log (
    audit_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    agent_name VARCHAR(100) NOT NULL,
    agent_type VARCHAR(50) NOT NULL,
    action VARCHAR(255) NOT NULL,
    target_entity VARCHAR(255),
    request_params JSONB,
    response_status VARCHAR(50),
    response_time_ms INTEGER,
    ip_address VARCHAR(45),
    anomaly_score FLOAT,
    is_anomalous BOOLEAN DEFAULT FALSE,
    metadata JSONB
);

SELECT create_hypertable('agent_audit_log', 'timestamp', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_audit_agent_name ON agent_audit_log (agent_name);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON agent_audit_log (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_anomalous ON agent_audit_log (is_anomalous) WHERE is_anomalous = TRUE;

-- Create notification log
CREATE TABLE IF NOT EXISTS notification_log (
    notification_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    vehicle_id INTEGER REFERENCES vehicles(vehicle_id),
    notification_type VARCHAR(50) NOT NULL,
    channel VARCHAR(50) NOT NULL,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    delivered BOOLEAN DEFAULT FALSE,
    read BOOLEAN DEFAULT FALSE,
    message_content TEXT,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_notification_customer ON notification_log (customer_id);
CREATE INDEX IF NOT EXISTS idx_notification_sent_at ON notification_log (sent_at DESC);

-- Insert sample data for service centers
INSERT INTO service_centers (name, address, city, state, zip_code, phone, email, capacity, latitude, longitude)
VALUES 
    ('Downtown Service Center', '123 Main St', 'Springfield', 'IL', '62701', '555-0101', 'downtown@pmi.com', 15, 39.7817, -89.6501),
    ('West Side Auto Care', '456 Oak Ave', 'Springfield', 'IL', '62704', '555-0102', 'westside@pmi.com', 12, 39.7995, -89.6815),
    ('North Service Hub', '789 Elm Blvd', 'Springfield', 'IL', '62702', '555-0103', 'north@pmi.com', 20, 39.8156, -89.6440)
ON CONFLICT DO NOTHING;

-- Create materialized view for vehicle health summary
CREATE MATERIALIZED VIEW IF NOT EXISTS vehicle_health_summary AS
SELECT 
    v.vehicle_id,
    v.vin,
    v.make,
    v.model,
    v.year,
    COUNT(DISTINCT fp.prediction_id) as total_predictions,
    MAX(fp.failure_probability) as max_failure_probability,
    COUNT(DISTINCT a.appointment_id) as total_appointments,
    MAX(vt.time) as last_telemetry_time,
    AVG(vt.engine_temperature) as avg_engine_temp,
    AVG(vt.vibration_level) as avg_vibration
FROM vehicles v
LEFT JOIN failure_predictions fp ON v.vehicle_id = fp.vehicle_id
LEFT JOIN appointments a ON v.vehicle_id = a.vehicle_id
LEFT JOIN vehicle_telemetry vt ON v.vin = vt.vin
GROUP BY v.vehicle_id, v.vin, v.make, v.model, v.year;

CREATE UNIQUE INDEX ON vehicle_health_summary (vehicle_id);

-- Create function to refresh materialized view
CREATE OR REPLACE FUNCTION refresh_vehicle_health_summary()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY vehicle_health_summary;
END;
$$ LANGUAGE plpgsql;
