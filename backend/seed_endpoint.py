"""
Simple FastAPI app to seed the database via HTTP endpoint
Run this on Railway to seed the database
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Allow all origins for this simple seed endpoint
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "Seed endpoint ready", "database": os.getenv("DATABASE_URL", "Not set")[:50] + "..."}

@app.post("/seed")
async def seed_database_endpoint():
    """Seed the database with sample data"""
    try:
        from seed_dashboard_data import seed_database
        await seed_database()
        return {
            "status": "success",
            "message": "Database seeded successfully with 50 vehicles and related data"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error seeding database: {str(e)}")

@app.get("/check-db")
async def check_database():
    """Check database connection"""
    try:
        from data.database import AsyncSessionLocal
        from sqlalchemy import text
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(text("SELECT COUNT(*) as count FROM vehicles"))
            count = result.scalar()
            
            result2 = await db.execute(text("SELECT COUNT(*) as count FROM customers"))
            customer_count = result2.scalar()
            
            return {
                "status": "connected",
                "vehicles": count,
                "customers": customer_count,
                "database_url": os.getenv("DATABASE_URL", "Not set")[:60] + "..."
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "database_url": os.getenv("DATABASE_URL", "Not set")[:60] + "..."
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
