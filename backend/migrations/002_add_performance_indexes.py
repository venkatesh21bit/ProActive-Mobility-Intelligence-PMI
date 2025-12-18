"""
Database migration: Add indexes for performance optimization
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '002_add_performance_indexes'
down_revision = '001_add_auth_fields'
branch_labels = None
depends_on = None


def upgrade():
    """Add indexes for better query performance"""
    
    # Vehicles table indexes
    op.create_index('idx_vehicles_customer_id', 'vehicles', ['customer_id'])
    op.create_index('idx_vehicles_vin', 'vehicles', ['vin'])
    
    # Appointments table indexes
    op.create_index('idx_appointments_customer_id', 'appointments', ['customer_id'])
    op.create_index('idx_appointments_vehicle_id', 'appointments', ['vehicle_id'])
    op.create_index('idx_appointments_center_id', 'appointments', ['center_id'])
    op.create_index('idx_appointments_scheduled_time', 'appointments', ['scheduled_time'])
    op.create_index('idx_appointments_status', 'appointments', ['status'])
    
    # Composite index for common appointment queries
    op.create_index(
        'idx_appointments_customer_status',
        'appointments',
        ['customer_id', 'status']
    )
    
    # Service centers indexes
    op.create_index('idx_service_centers_city', 'service_centers', ['city'])
    op.create_index('idx_service_centers_state', 'service_centers', ['state'])
    
    # Vehicle telemetry indexes (for time-series queries)
    op.create_index('idx_telemetry_vehicle_time', 'vehicle_telemetry', ['vehicle_id', 'time'])
    op.create_index('idx_telemetry_vin', 'vehicle_telemetry', ['vin'])


def downgrade():
    """Remove performance indexes"""
    op.drop_index('idx_telemetry_vin', table_name='vehicle_telemetry')
    op.drop_index('idx_telemetry_vehicle_time', table_name='vehicle_telemetry')
    op.drop_index('idx_service_centers_state', table_name='service_centers')
    op.drop_index('idx_service_centers_city', table_name='service_centers')
    op.drop_index('idx_appointments_customer_status', table_name='appointments')
    op.drop_index('idx_appointments_status', table_name='appointments')
    op.drop_index('idx_appointments_scheduled_time', table_name='appointments')
    op.drop_index('idx_appointments_center_id', table_name='appointments')
    op.drop_index('idx_appointments_vehicle_id', table_name='appointments')
    op.drop_index('idx_appointments_customer_id', table_name='appointments')
    op.drop_index('idx_vehicles_vin', table_name='vehicles')
    op.drop_index('idx_vehicles_customer_id', table_name='vehicles')
