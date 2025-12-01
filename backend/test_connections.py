"""
Test database and Redis connectivity
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from config.settings import settings
import asyncpg
import redis.asyncio as redis


async def test_postgres():
    """Test PostgreSQL connection"""
    print("\n" + "="*60)
    print("Testing PostgreSQL Connection")
    print("="*60)
    print(f"Database URL: {settings.database_url}")
    print(f"Host: {settings.postgres_host}")
    print(f"Port: {settings.postgres_port}")
    print(f"Database: {settings.postgres_db}")
    print(f"User: {settings.postgres_user}")
    
    try:
        # Try direct asyncpg connection with SSL
        conn = await asyncpg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db,
            timeout=10,
            ssl='require'  # Railway requires SSL
        )
        
        # Test query
        version = await conn.fetchval('SELECT version()')
        print(f"\n✓ PostgreSQL Connection Successful!")
        print(f"Version: {version[:50]}...")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"\n✗ PostgreSQL Connection Failed!")
        print(f"Error: {type(e).__name__}: {e}")
        return False


async def test_redis():
    """Test Redis connection"""
    print("\n" + "="*60)
    print("Testing Redis Connection")
    print("="*60)
    print(f"Redis URL: {settings.redis_url}")
    print(f"Host: {settings.redis_host}")
    print(f"Port: {settings.redis_port}")
    
    try:
        client = await redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=10
        )
        
        # Test ping
        pong = await client.ping()
        info = await client.info()
        
        print(f"\n✓ Redis Connection Successful!")
        print(f"Redis Version: {info.get('redis_version', 'unknown')}")
        
        await client.close()
        return True
        
    except Exception as e:
        print(f"\n✗ Redis Connection Failed!")
        print(f"Error: {type(e).__name__}: {e}")
        return False


async def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║           Database Connectivity Test                     ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    postgres_ok = await test_postgres()
    redis_ok = await test_redis()
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print(f"PostgreSQL: {'✓ PASS' if postgres_ok else '✗ FAIL'}")
    print(f"Redis:      {'✓ PASS' if redis_ok else '✗ FAIL'}")
    print("="*60 + "\n")
    
    if postgres_ok and redis_ok:
        print("All connections successful! You can now start the services.")
        return 0
    else:
        print("Some connections failed. Check your credentials and network.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
