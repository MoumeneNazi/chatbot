from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import UserModel, JournalModel, User, Journal, Base
import os
import logging

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

# Create tables only if they don't exist
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_by_username(username: str, db: Session):
    try:
        logger.info(f"Fetching user by username: {username}")
        return db.query(UserModel).filter(UserModel.username == username).first()
    except Exception as e:
        logger.error(f"Error fetching user by username: {str(e)}")
        return None

def create_user(user: UserModel, db: Session):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_all_users(db: Session):
    try:
        logger.info("Fetching all users")
        users = db.query(UserModel).all()
        logger.info(f"Found {len(users)} users")
        return users
    except Exception as e:
        logger.error(f"Error fetching all users: {str(e)}")
        return []

def promote_user(username: str, db: Session):
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

def get_journal_by_username(username: str, db: Session):
    try:
        logger.info(f"Fetching journal entries for user: {username}")
        entries = db.query(JournalModel).filter(JournalModel.username == username).all()
        logger.info(f"Found {len(entries)} journal entries")
        return entries
    except Exception as e:
        logger.error(f"Error fetching journal entries: {str(e)}")
        return []

def create_journal_entry(journal: JournalModel, db: Session):
    db.add(journal)
    db.commit()
    db.refresh(journal)
    return journal