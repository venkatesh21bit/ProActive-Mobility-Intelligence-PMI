"""
Apply database migrations manually
Run this script to add authentication fields to the customers table
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from data.database import async_engine, get_db_session
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def apply_migrations():
    """Apply database migrations"""
    
    async with async_engine.begin() as conn:
        logger.info("Starting database migrations...")
        
        try:
            # Check if columns already exist
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'customers' 
                AND column_name = 'password_hash'
            """))
            
            if result.fetchone():
                logger.info("✅ password_hash column already exists")
            else:
                logger.info("Adding authentication fields to customers table...")
                
                # Add password_hash column
                await conn.execute(text("""
                    ALTER TABLE customers 
                    ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)
                """))
                logger.info("✅ Added password_hash column")
                
                # Add role column
                await conn.execute(text("""
                    ALTER TABLE customers 
                    ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'customer' NOT NULL
                """))
                logger.info("✅ Added role column")
                
                # Add is_active column
                await conn.execute(text("""
                    ALTER TABLE customers 
                    ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true NOT NULL
                """))
                logger.info("✅ Added is_active column")
                
                # Add email_verified column
                await conn.execute(text("""
                    ALTER TABLE customers 
                    ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT false NOT NULL
                """))
                logger.info("✅ Added email_verified column")
                
                # Add last_login column
                await conn.execute(text("""
                    ALTER TABLE customers 
                    ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE
                """))
                logger.info("✅ Added last_login column")
                
                # Create indexes
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_customers_email 
                    ON customers(email)
                """))
                logger.info("✅ Created email index")
                
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_customers_role 
                    ON customers(role)
                """))
                logger.info("✅ Created role index")
                
            # Check and add performance indexes if needed
            logger.info("Adding performance indexes...")
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_predictions_vehicle_timestamp 
                ON failure_predictions(vehicle_id, prediction_timestamp DESC)
            """))
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_bookings_customer 
                ON bookings(customer_id)
            """))
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_bookings_vehicle 
                ON bookings(vehicle_id)
            """))
            
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_notifications_customer 
                ON notification_logs(customer_id)
            """))
            
            logger.info("✅ All performance indexes created")
            
            logger.info("🎉 Database migrations completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(apply_migrations())
