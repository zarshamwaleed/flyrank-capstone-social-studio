import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="social_media_studio",
        user="postgres",
        password="postgres"
    )
    cur = conn.cursor()
    cur.execute("SELECT version()")
    version = cur.fetchone()[0]
    print(f"✅ Connected to PostgreSQL: {version}")
    
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = [row[0] for row in cur.fetchall()]
    print(f"📋 Tables: {', '.join(tables)}")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")
