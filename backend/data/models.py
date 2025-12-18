from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ARRAY, ForeignKey, DECIMAL, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class Customer(Base):
    __tablename__ = 'customers'
    
    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255))  # For JWT authentication
    phone = Column(String(20))
    address = Column(Text)
    role = Column(String(50), default='customer')  # Role for RBAC
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    vehicles = relationship("Vehicle", back_populates="customer")
    appointments = relationship("Appointment", back_populates="customer")


class Vehicle(Base):
    __tablename__ = 'vehicles'
    
    vehicle_id = Column(Integer, primary_key=True, autoincrement=True)
    vin = Column(String(17), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'))
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    mileage = Column(Integer, default=0)
    purchase_date = Column(DateTime(timezone=True))
    warranty_expiry = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="vehicles")
    appointments = relationship("Appointment", back_populates="vehicle")
    predictions = relationship("FailurePrediction", back_populates="vehicle")
    maintenance_records = relationship("MaintenanceRecord", back_populates="vehicle")


class VehicleTelemetry(Base):
    __tablename__ = 'vehicle_telemetry'
    
    time = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    vehicle_id = Column(String(50), primary_key=True, nullable=False)
    vin = Column(String(17), nullable=False)
    engine_temperature = Column(Float)
    coolant_temperature = Column(Float)
    oil_pressure = Column(Float)
    vibration_level = Column(Float)
    rpm = Column(Integer)
    speed = Column(Float)
    fuel_level = Column(Float)
    battery_voltage = Column(Float)
    odometer = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)
    meta_data = Column('metadata', JSON)


class ServiceCenter(Base):
    __tablename__ = 'service_centers'
    
    center_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(10))
    phone = Column(String(20))
    email = Column(String(255))
    capacity = Column(Integer, default=10)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    appointments = relationship("Appointment", back_populates="service_center")


class Appointment(Base):
    __tablename__ = 'appointments'
    
    appointment_id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.vehicle_id'))
    customer_id = Column(Integer, ForeignKey('customers.customer_id'))
    center_id = Column(Integer, ForeignKey('service_centers.center_id'))
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    appointment_type = Column(String(50), nullable=False)
    status = Column(String(50), default='scheduled')
    predicted_issue = Column(Text)
    actual_issue = Column(Text)
    estimated_duration_minutes = Column(Integer)
    actual_duration_minutes = Column(Integer)
    cost = Column(DECIMAL(10, 2))
    customer_consent = Column(Boolean, default=False)
    consent_timestamp = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="appointments")
    customer = relationship("Customer", back_populates="appointments")
    service_center = relationship("ServiceCenter", back_populates="appointments")
    maintenance_records = relationship("MaintenanceRecord", back_populates="appointment")


class RCACapaRecord(Base):
    __tablename__ = 'rca_capa_records'
    
    record_id = Column(Integer, primary_key=True, autoincrement=True)
    incident_date = Column(DateTime(timezone=True), nullable=False)
    vehicle_id = Column(Integer, ForeignKey('vehicles.vehicle_id'))
    vin = Column(String(17))
    component_name = Column(String(255), nullable=False)
    failure_mode = Column(String(255), nullable=False)
    root_cause = Column(Text, nullable=False)
    corrective_action = Column(Text)
    preventive_action = Column(Text)
    severity = Column(String(50))
    occurrence_count = Column(Integer, default=1)
    design_change_required = Column(Boolean, default=False)
    manufacturing_process_change = Column(Boolean, default=False)
    supplier = Column(String(255))
    part_number = Column(String(100))
    # embedding_vector would need pgvector extension in production
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class MaintenanceRecord(Base):
    __tablename__ = 'maintenance_records'
    
    maintenance_id = Column(Integer, primary_key=True, autoincrement=True)
    appointment_id = Column(Integer, ForeignKey('appointments.appointment_id'))
    vehicle_id = Column(Integer, ForeignKey('vehicles.vehicle_id'))
    service_date = Column(DateTime(timezone=True), nullable=False)
    service_type = Column(String(100), nullable=False)
    components_replaced = Column(ARRAY(Text))
    labor_hours = Column(DECIMAL(5, 2))
    parts_cost = Column(DECIMAL(10, 2))
    labor_cost = Column(DECIMAL(10, 2))
    total_cost = Column(DECIMAL(10, 2))
    technician_notes = Column(Text)
    customer_feedback = Column(Text)
    feedback_rating = Column(Integer, CheckConstraint('feedback_rating >= 1 AND feedback_rating <= 5'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    appointment = relationship("Appointment", back_populates="maintenance_records")
    vehicle = relationship("Vehicle", back_populates="maintenance_records")


class FailurePrediction(Base):
    __tablename__ = 'failure_predictions'
    
    prediction_id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.vehicle_id'))
    vin = Column(String(17), nullable=False)
    prediction_time = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    predicted_component = Column(String(255), nullable=False)
    failure_probability = Column(Float, nullable=False)
    severity = Column(String(50), nullable=False)
    estimated_days_to_failure = Column(Integer)
    confidence_score = Column(Float)
    model_version = Column(String(50))
    feature_importance = Column(JSON)
    explanation = Column(Text)
    action_taken = Column(String(100))
    actual_failure = Column(Boolean)
    actual_failure_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="predictions")


class AgentAuditLog(Base):
    __tablename__ = 'agent_audit_log'
    
    audit_id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    agent_name = Column(String(100), nullable=False)
    agent_type = Column(String(50), nullable=False)
    action = Column(String(255), nullable=False)
    target_entity = Column(String(255))
    request_params = Column(JSON)
    response_status = Column(String(50))
    response_time_ms = Column(Integer)
    ip_address = Column(String(45))
    anomaly_score = Column(Float)
    is_anomalous = Column(Boolean, default=False)
    meta_data = Column('metadata', JSON)


class NotificationLog(Base):
    __tablename__ = 'notification_log'
    
    notification_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'))
    vehicle_id = Column(Integer, ForeignKey('vehicles.vehicle_id'))
    notification_type = Column(String(50), nullable=False)
    channel = Column(String(50), nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    delivered = Column(Boolean, default=False)
    read = Column(Boolean, default=False)
    message_content = Column(Text)
    meta_data = Column('metadata', JSON)
