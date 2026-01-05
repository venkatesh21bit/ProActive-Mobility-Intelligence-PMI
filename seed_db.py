#!/usr/bin/env python3
"""
Simple database seeding script for Railway deployment
Run this after deploying: railway run --service ProActive-Mobility-Intelligence-PMI python seed_db.py
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, 'backend')

async def main():
    print("=" * 60)
    print("Starting Railway Database Seeding")
    print("=" * 60)
    
    try:
        from backend.seed_dashboard_data import seed_database
        
        print("\n✓ Imported seed_database function")
        print(f"✓ Database URL: {os.getenv('DATABASE_URL', 'Not set')[:50]}...")
        
        print("\n⏳ Seeding database...")
        await seed_database()
        
        print("\n" + "=" * 60)
        print("✅ Database seeded successfully!")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Error seeding database: {str(e)}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
