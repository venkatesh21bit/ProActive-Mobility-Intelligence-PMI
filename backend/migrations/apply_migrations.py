"""
Apply database migrations
"""

import sys
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from data.database import get_db_url
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def apply_migrations():
    """Apply database migrations"""
    database_url = get_db_url()
    engine = create_async_engine(database_url, echo=True)
    
    try:
        async with engine.begin() as conn:
            logger.info("Applying migration: Add authentication fields")
            
            # Check if columns already exist
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'customers' AND column_name = 'password_hash'
            """))
            exists = result.fetchone()
            
            if not exists:
                # Add password_hash column
                await conn.execute(text(
                    "ALTER TABLE customers ADD COLUMN password_hash VARCHAR(255)"
                ))
                
                # Add role column
                await conn.execute(text(
                    "ALTER TABLE customers ADD COLUMN role VARCHAR(50) DEFAULT 'customer'"
                ))
                
                # Add is_active column
                await conn.execute(text(
                    "ALTER TABLE customers ADD COLUMN is_active BOOLEAN DEFAULT true"
                ))
                
                # Add email_verified column
                await conn.execute(text(
                    "ALTER TABLE customers ADD COLUMN email_verified BOOLEAN DEFAULT false"
                ))
                
                # Add last_login column
                await conn.execute(text(
                    "ALTER TABLE customers ADD COLUMN last_login TIMESTAMP WITH TIME ZONE"
                ))
                
                logger.info("✓ Authentication fields added")
            else:
                logger.info("✓ Authentication fields already exist")
            
            # Add indexes
            logger.info("Adding performance indexes...")
            
            # Create indexes if they don't exist
            indexes = [
                ("idx_customers_email", "CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email)"),
                ("idx_customers_role", "CREATE INDEX IF NOT EXISTS idx_customers_role ON customers(role)"),
                ("idx_vehicles_customer_id", "CREATE INDEX IF NOT EXISTS idx_vehicles_customer_id ON vehicles(customer_id)"),
                ("idx_vehicles_vin", "CREATE INDEX IF NOT EXISTS idx_vehicles_vin ON vehicles(vin)"),
                ("idx_appointments_customer_id", "CREATE INDEX IF NOT EXISTS idx_appointments_customer_id ON appointments(customer_id)"),
                ("idx_appointments_vehicle_id", "CREATE INDEX IF NOT EXISTS idx_appointments_vehicle_id ON appointments(vehicle_id)"),
                ("idx_appointments_status", "CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status)"),
            ]
            
            for idx_name, idx_sql in indexes:
                try:
                    await conn.execute(text(idx_sql))
                    logger.info(f"✓ Created index: {idx_name}")
                except Exception as e:
                    logger.warning(f"Index {idx_name} may already exist: {e}")
            
            logger.info("✓ All migrations applied successfully")
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(apply_migrations())
