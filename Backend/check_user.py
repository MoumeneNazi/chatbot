from sqlalchemy.orm import Session
from database import SessionLocal, get_user_by_username
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_user(username: str, db: Session):
    try:
        # Get user
        user = get_user_by_username(username, db)
        if not user:
            print(f"User not found: {username}")
            return
            
        print(f"\nUser Details:")
        print(f"Username: {user.username}")
        print(f"Role: {user.role}")
        print(f"ID: {user.id}")
        print(f"Created at: {user.created_at}")
        print(f"Last login: {user.last_login}")
        
    except Exception as e:
        print(f"Error checking user: {str(e)}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python check_user.py <username>")
        sys.exit(1)
        
    username = sys.argv[1]
    db = SessionLocal()
    try:
        check_user(username, db)
    finally:
        db.close()

if __name__ == "__main__":
    main() 