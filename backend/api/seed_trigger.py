"""
Seed trigger endpoint for database initialization
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import asyncio
import os

router = APIRouter()

@router.post("/trigger-seed")
async def trigger_seed(authorization: Optional[str] = Header(None)):
    """
    Trigger database seeding (protected endpoint)
    Only works if ALLOW_SEED environment variable is set to 'true'
    """
    # Check if seeding is allowed
    if os.getenv("ALLOW_SEED") != "true":
        raise HTTPException(
            status_code=403, 
            detail="Database seeding is not enabled. Set ALLOW_SEED=true to enable."
        )
    
    try:
        # Import here to avoid circular dependencies
        from seed_dashboard_data import seed_dashboard
        
        # Run seeding
        await seed_dashboard()
        
        return {
            "status": "success",
            "message": "Database seeded successfully with demo data"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error seeding database: {str(e)}"
        )

@router.get("/seed-status")
async def seed_status():
    """Check if seeding is enabled"""
    return {
        "seed_enabled": os.getenv("ALLOW_SEED") == "true",
        "environment": os.getenv("ENVIRONMENT", "unknown")
    }
