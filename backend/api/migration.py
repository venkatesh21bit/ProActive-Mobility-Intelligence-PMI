"""
Database Migration API Endpoint
Run migrations through the deployed Cloud Run service
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from data.database import get_db_session
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/migrate")
async def run_migrations(db: AsyncSession = Depends(get_db_session)):
    """
    Apply database migrations
    Adds authentication fields to customers table
    """
    try:
        logger.info("Starting database migrations...")
        
        # Check if columns already exist
        result = await db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'customers' 
            AND column_name = 'password_hash'
        """))
        
        if result.fetchone():
            return {
                "status": "success",
                "message": "Migrations already applied",
                "changes": []
            }
        
        changes = []
        
        # Add password_hash column
        await db.execute(text("""
            ALTER TABLE customers 
            ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)
        """))
        changes.append("Added password_hash column")
        
        # Add role column
        await db.execute(text("""
            ALTER TABLE customers 
            ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'customer' NOT NULL
        """))
        changes.append("Added role column")
        
        # Add is_active column
        await db.execute(text("""
            ALTER TABLE customers 
            ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true NOT NULL
        """))
        changes.append("Added is_active column")
        
        # Add email_verified column
        await db.execute(text("""
            ALTER TABLE customers 
            ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT false NOT NULL
        """))
        changes.append("Added email_verified column")
        
        # Add last_login column
        await db.execute(text("""
            ALTER TABLE customers 
            ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE
        """))
        changes.append("Added last_login column")
        
        # Create indexes
        await db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_customers_email 
            ON customers(email)
        """))
        changes.append("Created email index")
        
        await db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_customers_role 
            ON customers(role)
        """))
        changes.append("Created role index")
        
        await db.commit()
        
        logger.info(f"✅ Migrations completed: {len(changes)} changes")
        
        return {
            "status": "success",
            "message": "Database migrations completed successfully",
            "changes": changes
        }
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")
