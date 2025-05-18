from sqlalchemy.orm import Session
from database import SessionLocal, get_user_by_username
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def promote_to_therapist(username: str, db: Session):
    try:
        # Get user
        user = get_user_by_username(username, db)
        if not user:
            logger.error(f"User not found: {username}")
            return False
            
        # Check if already therapist
        if user.role == "therapist":
            logger.info(f"User {username} is already a therapist")
            return True
            
        # Update role
        user.role = "therapist"
        db.commit()
        logger.info(f"Successfully promoted {username} to therapist role")
        return True
    except Exception as e:
        logger.error(f"Error promoting user: {str(e)}")
        db.rollback()
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python promote_therapist.py <username>")
        sys.exit(1)
        
    username = sys.argv[1]
    db = SessionLocal()
    try:
        if promote_to_therapist(username, db):
            print(f"Successfully promoted {username} to therapist role")
        else:
            print(f"Failed to promote {username}")
    finally:
        db.close()

if __name__ == "__main__":
    main() 