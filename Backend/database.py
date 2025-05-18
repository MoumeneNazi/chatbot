from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker, Session
from models import UserModel, JournalModel, User, Journal, Base
from datetime import datetime
import os
import logging
from typing import List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the database directory if it doesn't exist
DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(DB_DIR, "users.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE}"

# Ensure the directory exists
os.makedirs(DB_DIR, exist_ok=True)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_by_username(username: str, db: Session) -> Optional[UserModel]:
    try:
        logger.info(f"Fetching user by username: {username}")
        return db.query(UserModel).filter(UserModel.username == username).first()
    except Exception as e:
        logger.error(f"Error fetching user by username: {str(e)}")
        return None

def get_user_by_id(user_id: int, db: Session) -> Optional[UserModel]:
    try:
        logger.info(f"Fetching user by ID: {user_id}")
        return db.query(UserModel).filter(UserModel.id == user_id).first()
    except Exception as e:
        logger.error(f"Error fetching user by ID: {str(e)}")
        return None

def create_user(user: UserModel, db: Session) -> Optional[UserModel]:
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        db.rollback()
        return None

def get_all_users(db: Session) -> List[UserModel]:
    try:
        logger.info("Fetching all users")
        users = db.query(UserModel).all()
        logger.info(f"Found {len(users)} users")
        return users
    except Exception as e:
        logger.error(f"Error fetching all users: {str(e)}")
        return []

def update_user_login(user: UserModel, db: Session) -> bool:
    try:
        logger.info(f"Updating last login for user: {user.username}")
        user.last_login = datetime.utcnow()
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Error updating user login: {str(e)}")
        db.rollback()
        return False

def promote_user(username: str, db: Session) -> Optional[UserModel]:
    try:
        logger.info(f"Promoting user: {username}")
        user = db.query(UserModel).filter(UserModel.username == username).first()
        if user:
            user.role = "therapist"
            db.commit()
            db.refresh(user)
            logger.info(f"Successfully promoted user: {username}")
            return user
        logger.warning(f"User not found for promotion: {username}")
        return None
    except Exception as e:
        logger.error(f"Error promoting user: {str(e)}")
        db.rollback()
        return None

def get_journal_entries(user_id: int, db: Session) -> List[JournalModel]:
    try:
        logger.info(f"Fetching journal entries for user ID: {user_id}")
        entries = db.query(JournalModel).filter(JournalModel.user_id == user_id).all()
        logger.info(f"Found {len(entries)} journal entries")
        return entries
    except Exception as e:
        logger.error(f"Error fetching journal entries: {str(e)}")
        return []

def create_journal_entry(journal: JournalModel, db: Session) -> Optional[JournalModel]:
    try:
        db.add(journal)
        db.commit()
        db.refresh(journal)
        return journal
    except Exception as e:
        logger.error(f"Error creating journal entry: {str(e)}")
        db.rollback()
        return None

def delete_user(username: str, db: Session) -> bool:
    try:
        logger.info(f"Deleting user: {username}")
        user = db.query(UserModel).filter(UserModel.username == username).first()
        if user:
            db.delete(user)
            db.commit()
            logger.info(f"Successfully deleted user: {username}")
            return True
        logger.warning(f"User not found for deletion: {username}")
        return False
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        db.rollback()
        return False