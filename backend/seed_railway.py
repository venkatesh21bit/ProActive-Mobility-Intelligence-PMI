#!/usr/bin/env python3
"""
Seed Railway Database Script
Run this to populate the Railway database with sample data
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))


async def main():
    """Main seed function"""
    print("=" * 60)
    print("🌱 Seeding Railway Database")
    print("=" * 60)
    print()
    
    try:
        # Import after path is set
        from seed_dashboard_data import seed_database
        
        # Run seeding
        await seed_database()
        
        print("\n" + "=" * 60)
        print("✅ Database seeding completed successfully!")
        print("=" * 60)
        print("\n🎉 Your Railway database is now populated with sample data!")
        print("\nWhat was added:")
        print("  • Sample customers")
        print("  • Service centers")
        print("  • 50 Hero MotoCorp vehicles")
        print("  • Vehicle telemetry data")
        print("  • Failure predictions")
        print("  • Appointments")
        print("\n🚀 You can now test your application!")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
