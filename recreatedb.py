import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from backend.app import models, database

# Verify connection string is loaded
db_url = os.getenv("DATABASE_URL")
print(f"📡 Database URL: {db_url}")

if not db_url:
    print("❌ ERROR: DATABASE_URL not found in .env file!")
    print("Make sure your .env file exists and has DATABASE_URL set")
    exit(1)

try:
    print("🔄 Dropping old tables...")
    models.Base.metadata.drop_all(bind=database.engine)
    print("✅ Old tables dropped")
    
    print("🔄 Creating new tables...")
    models.Base.metadata.create_all(bind=database.engine)
    print("✅ New tables created successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)