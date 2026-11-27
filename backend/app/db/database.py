import os
import logging
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Load .env from backend directory or project root
load_dotenv(find_dotenv(usecwd=True))

logger = logging.getLogger(__name__)

database_url = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Normalize PostgreSQL driver for NeonDB / psycopg
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
elif database_url.startswith("postgresql://") and not database_url.startswith("postgresql+"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(
    database_url,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initializes PostgreSQL database with pgvector extension and creates all tables.
    Safe to run repeatedly on startup or during automated EC2 provisioning.
    """
    from app.db.base import Base
    import app.models  # Registers all SQLAlchemy models with Base.metadata

    # Enable pgvector if connecting to PostgreSQL
    if "postgres" in str(engine.url):
        try:
            with engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                conn.commit()
                logger.info("pgvector extension verified/enabled.")
        except Exception as e:
            logger.warning(f"Note: pgvector extension create check: {e}")

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.error(f"Error during Base.metadata.create_all: {e}")
        raise
