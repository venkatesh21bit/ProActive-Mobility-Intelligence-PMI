#!/usr/bin/env python3
"""
Railway Database Setup Script
Run this using Railway CLI after deployment:
    railway run python setup_railway_db.py
"""

import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))


async def setup_database():
    """Initialize database with tables and demo data"""
    print("🚀 Setting up Railway Database...")
    
    try:
        from data.database import init_db, AsyncSessionLocal
        from data.models import Base
        from sqlalchemy import text
        
        # Initialize database
        print("📊 Initializing database tables...")
        await init_db()
        print("✅ Database tables created successfully!")
        
        # Check if TimescaleDB extension is available
        print("🔍 Checking TimescaleDB extension...")
        async with AsyncSessionLocal() as session:
            try:
                # Try to enable TimescaleDB
                await session.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))
                await session.commit()
                print("✅ TimescaleDB extension enabled!")
            except Exception as e:
                print(f"⚠️ TimescaleDB not available (this is OK): {e}")
                print("   Using regular PostgreSQL tables...")
        
        # Try to seed demo data if script exists
        print("\n📝 Attempting to seed demo data...")
        try:
            # Import and run seed script
            seed_script = backend_dir / "seed_demo.sql"
            if seed_script.exists():
                print("   Running seed_demo.sql...")
                with open(seed_script, 'r') as f:
                    sql_commands = f.read()
                
                async with AsyncSessionLocal() as session:
                    # Split and execute SQL commands
                    for command in sql_commands.split(';'):
                        if command.strip():
                            await session.execute(text(command))
                    await session.commit()
                print("✅ Demo data seeded successfully!")
            else:
                print("   No seed file found, skipping...")
        except Exception as e:
            print(f"⚠️ Could not seed demo data: {e}")
            print("   You can add data manually later...")
        
        print("\n" + "="*50)
        print("🎉 Database setup complete!")
        print("="*50)
        return True
        
    except Exception as e:
        print(f"\n❌ Error setting up database: {e}")
        print("\nTroubleshooting:")
        print("1. Check DATABASE_URL is set correctly")
        print("2. Ensure PostgreSQL service is running")
        print("3. Verify network connectivity between services")
        return False


async def verify_connection():
    """Verify database connection"""
    print("\n🔍 Verifying database connection...")
    
    try:
        from data.database import AsyncSessionLocal
        from sqlalchemy import text
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"✅ Connected to PostgreSQL!")
            print(f"   Version: {version[:50]}...")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def check_environment():
    """Check required environment variables"""
    print("🔍 Checking environment variables...")
    
    required_vars = [
        "DATABASE_URL",
        "REDIS_URL",
        "SECRET_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            print(f"   ❌ {var} - Missing")
        else:
            # Don't print actual values for security
            print(f"   ✅ {var} - Set")
    
    if missing_vars:
        print(f"\n⚠️ Missing required variables: {', '.join(missing_vars)}")
        print("   Add them in Railway dashboard: Service → Variables")
        return False
    
    print("✅ All required variables are set!")
    return True


async def main():
    """Main setup function"""
    print("="*50)
    print("🚂 Railway Database Setup")
    print("="*50)
    print()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Verify connection
    if not await verify_connection():
        print("\n💡 Tip: Make sure PostgreSQL service is running in Railway")
        sys.exit(1)
    
    # Setup database
    success = await setup_database()
    
    if success:
        print("\n✨ You're all set! Your database is ready.")
        sys.exit(0)
    else:
        print("\n⚠️ Setup completed with warnings. Check messages above.")
        sys.exit(1)


if __name__ == "__main__":
    # Check if we're in Railway environment
    if not os.getenv("RAILWAY_ENVIRONMENT"):
        print("⚠️ Warning: Not running in Railway environment")
        print("   This script is designed to run on Railway")
        print("   Run it using: railway run python setup_railway_db.py")
        print()
        
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)
    
    asyncio.run(main())
