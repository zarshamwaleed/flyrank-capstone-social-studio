from app.database import engine
from app.models import Base
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_database():
    print("=" * 50)
    print("Creating Database Tables...")
    print("=" * 50)
    
    try:
        # Create all tables
        print("📊 Creating tables: posts, variants, publish_attempts...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        print("   - posts")
        print("   - variants")
        print("   - publish_attempts")
        print("=" * 50)
        print("✅ Database initialization complete!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        print("=" * 50)

if __name__ == "__main__":
    init_database()
