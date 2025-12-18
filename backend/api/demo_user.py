"""
Create demo user directly in database
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from data.database import get_db_session
from auth.security import get_password_hash

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/create-demo-user")
async def create_demo_user(db: AsyncSession = Depends(get_db_session)):
    """Create a demo user with vehicle for testing"""
    try:
        # Check if user exists
        result = await db.execute(text("""
            SELECT customer_id FROM customers WHERE email = 'demo@pmi.com'
        """))
        
        customer_row = result.fetchone()
        
        if customer_row:
            customer_id = customer_row[0]
            # Update existing user with Indian phone number
            await db.execute(text("""
                UPDATE customers 
                SET phone = '+919025447567',
                    role = 'customer',
                    is_active = true,
                    email_verified = true
                WHERE email = 'demo@pmi.com'
            """))
            message = "Demo user updated with phone +919025447567"
        else:
            # Insert new user
            await db.execute(text("""
                INSERT INTO customers (
                    email, first_name, last_name, phone, 
                    role, is_active, email_verified
                ) VALUES (
                    'demo@pmi.com', 'Demo', 'User', '+919025447567',
                    'customer', true, true
                )
            """))
            result = await db.execute(text("""
                SELECT customer_id FROM customers WHERE email = 'demo@pmi.com'
            """))
            customer_id = result.fetchone()[0]
            message = "Demo user created"
        
        # Check if customer has a vehicle - connect to existing Hero MotoCorp vehicle
        vehicle_result = await db.execute(text("""
            SELECT vehicle_id FROM vehicles WHERE vehicle_id = 3
        """))
        
        vehicle_row = vehicle_result.fetchone()
        
        if vehicle_row:
            # Update vehicle to belong to demo customer
            await db.execute(text("""
                UPDATE vehicles 
                SET customer_id = :cid
                WHERE vehicle_id = 3
            """), {"cid": customer_id})
            
            # Update all references from old Toyota Camry (53) to Hero MotoCorp (3)
            await db.execute(text("""
                UPDATE appointments 
                SET vehicle_id = 3
                WHERE vehicle_id = 53 AND customer_id = :cid
            """), {"cid": customer_id})
            
            await db.execute(text("""
                UPDATE notification_log 
                SET vehicle_id = 3
                WHERE vehicle_id = 53 AND customer_id = :cid
            """), {"cid": customer_id})
            
            await db.execute(text("""
                UPDATE failure_predictions 
                SET vehicle_id = 3
                WHERE vehicle_id = 53
            """), {"cid": customer_id})
            
            # Delete the old Toyota Camry demo vehicle
            await db.execute(text("""
                DELETE FROM vehicles 
                WHERE vin = 'DEMO1234567890123' AND customer_id = :cid
            """), {"cid": customer_id})
            
            message += " and connected to Hero MotoCorp Super Splendor (vehicle_id: 3)"
        else:
            message += " but vehicle 3 not found in fleet"
        
        await db.commit()
        
        return {
            "status": "success",
            "message": message,
            "email": "demo@pmi.com",
            "phone": "+919025447567",
            "password": "demo123"
        }
        
    except Exception as e:
        await db.rollback()
        return {
            "status": "error",
            "message": str(e)
        }
