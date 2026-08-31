from app.database import engine
from app.models import Base

print("=" * 50)
print("Creating SQLite Tables...")
print("=" * 50)

try:
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")
    print("   - posts")
    print("   - variants")
    print("   - publish_attempts")
    print("=" * 50)
except Exception as e:
    print(f"❌ Error: {e}")
