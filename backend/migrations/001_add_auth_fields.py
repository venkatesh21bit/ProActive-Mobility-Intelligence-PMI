"""
Database migration: Add authentication fields to customers table
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_add_auth_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add authentication fields to customers table"""
    # Add password_hash column
    op.add_column('customers', sa.Column('password_hash', sa.String(255), nullable=True))
    
    # Add role column with default value
    op.add_column('customers', sa.Column('role', sa.String(50), nullable=False, server_default='customer'))
    
    # Add is_active column
    op.add_column('customers', sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'))
    
    # Add email_verified column
    op.add_column('customers', sa.Column('email_verified', sa.Boolean, nullable=False, server_default='false'))
    
    # Add last_login column
    op.add_column('customers', sa.Column('last_login', sa.DateTime(timezone=True), nullable=True))
    
    # Add index on email for faster lookups
    op.create_index('idx_customers_email', 'customers', ['email'])
    
    # Add index on role for RBAC queries
    op.create_index('idx_customers_role', 'customers', ['role'])


def downgrade():
    """Remove authentication fields from customers table"""
    op.drop_index('idx_customers_role', table_name='customers')
    op.drop_index('idx_customers_email', table_name='customers')
    op.drop_column('customers', 'last_login')
    op.drop_column('customers', 'email_verified')
    op.drop_column('customers', 'is_active')
    op.drop_column('customers', 'role')
    op.drop_column('customers', 'password_hash')
