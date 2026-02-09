"""
Database Initialization Script
Creates the database and initial tables
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Add parent directory to path to import app modules
sys.path.insert(0, 'e:/AI Meeter/backend')

from app.core.config import settings
from app.db.base import Base
from app.models.user import User  # Import all models to register them


async def init_db():
    """
    Initialize the database and create all tables
    """
    # Replace postgresql:// with postgresql+asyncpg:// for async
    database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    
    print(f"🔧 Connecting to database...")
    engine = create_async_engine(database_url, echo=True)
    
    try:
        # Test connection
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
        
        # Create all tables
        print("\n📋 Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database tables created successfully!")
        print("\n📊 Tables created:")
        print("  - users")
        
        # Show table info
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = result.fetchall()
            
            if tables:
                print("\n📝 Existing tables in database:")
                for table in tables:
                    print(f"  ✓ {table[0]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        await engine.dispose()
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("AI Meeting Automation - Database Initialization")
    print("=" * 60)
    
    result = asyncio.run(init_db())
    
    if result:
        print("\n" + "=" * 60)
        print("✅ Database initialization complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Start the backend server: uvicorn app.main:app --reload")
        print("2. Start the frontend: npm run dev")
        print("3. Open http://localhost:3000")
    else:
        print("\n❌ Database initialization failed. Please check your configuration.")
        sys.exit(1)
