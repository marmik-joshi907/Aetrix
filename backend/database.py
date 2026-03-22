import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import config

logger = logging.getLogger(__name__)

# Set up PostgreSQL engine
# echo=False prevents logging every single SQL query, which can be noisy
engine = create_engine(config.DATABASE_URL, echo=False)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model for future SQLAlchemy classes
Base = declarative_base()

def get_db():
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """Verify database connection on startup."""
    try:
        db = SessionLocal()
        db.execute(text('SELECT 1'))
        logger.info("✅ Successfully connected to PostgreSQL database.")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to connect to PostgreSQL: {e}")
        return False
    finally:
        db.close()
