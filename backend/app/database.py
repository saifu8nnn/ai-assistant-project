import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Load the secrets from the .env file located one folder up (in the root directory)
load_dotenv(dotenv_path="../.env")

# 2. Get the specific pieces from the .env file
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")

# 3. Assemble the local URL for Alembic using those secrets
LOCAL_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@localhost:5432/{DB_NAME}"

# 4. If running inside Docker, use the Docker URL. Otherwise, fallback to our secure local URL.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", LOCAL_URL)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()