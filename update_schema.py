from app.database import engine, Base
from app.models import PublishAttempt, Variant, Post
import sqlite3
import os

def update_database():
    print("Updating database schema...")
    
    # Check if we're using SQLite
    db_url = os.getenv("DATABASE_URL", "sqlite:///./social_media_studio.db")
    
    if db_url.startswith("sqlite"):
        db_path = db_url.replace("sqlite:///", "")
        print(f"Using SQLite database: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if publish_attempts table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='publish_attempts'")
        if cursor.fetchone():
            print("publish_attempts table exists, checking columns...")
            
            # Get existing columns
            cursor.execute("PRAGMA table_info(publish_attempts)")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"Existing columns: {columns}")
            
            # Add missing columns
            if 'retry_count' not in columns:
                print("Adding retry_count column...")
                cursor.execute("ALTER TABLE publish_attempts ADD COLUMN retry_count INTEGER DEFAULT 0")
            
            if 'is_duplicate' not in columns:
                print("Adding is_duplicate column...")
                cursor.execute("ALTER TABLE publish_attempts ADD COLUMN is_duplicate BOOLEAN DEFAULT 0")
            
            if 'external_id' not in columns:
                print("Adding external_id column...")
                cursor.execute("ALTER TABLE publish_attempts ADD COLUMN external_id VARCHAR(255)")
            
            conn.commit()
            print("✅ Database schema updated successfully!")
        else:
            print("publish_attempts table does not exist, creating tables...")
            Base.metadata.create_all(bind=engine)
            print("✅ Tables created successfully!")
        
        conn.close()
    else:
        print("Using PostgreSQL, creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")

if __name__ == "__main__":
    update_database()
