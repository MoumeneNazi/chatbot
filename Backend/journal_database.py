from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the database directory if it doesn't exist
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(DB_DIR, "journals.db")
JOURNAL_DB_URL = f"sqlite:///{DB_FILE}"

# Ensure the directory exists
os.makedirs(DB_DIR, exist_ok=True)

JournalBase = declarative_base()
journal_engine = create_engine(JOURNAL_DB_URL, connect_args={"check_same_thread": False})
JournalSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=journal_engine)

def get_journal_db():
    db = JournalSessionLocal()
    try:
        yield db
    finally:
        db.close() 