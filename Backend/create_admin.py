#!/usr/bin/env python3
import sys
import os
import getpass
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from models import UserModel, Base
from datetime import datetime
from dotenv import load_dotenv
from passlib.context import CryptContext

# Password hashing settings - match the one in auth.py
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

# Get database URI from environment or default
DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///./mental_health.db")

def create_admin_user(username, email, password):
    # Connect to database
    engine = create_engine(DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if the username or email already exists
        existing_user = session.query(UserModel).filter(
            UserModel.username == username
        ).first()
        
        if existing_user:
            print(f"Error: A user with username '{username}' already exists.")
            return False
        
        # Create password hash
        hashed_password = get_password_hash(password)
        
        # Create admin user
        admin_user = UserModel(
            username=username,
            password=hashed_password,
            role="admin",
            created_at=datetime.utcnow()
        )
        
        # Add and commit
        session.add(admin_user)
        session.commit()
        
        print(f"Admin user '{username}' created successfully!")
        return True
    
    except Exception as e:
        session.rollback()
        print(f"Error creating admin user: {str(e)}")
        return False
    
    finally:
        session.close()

def main():
    print("\n=== Create Admin User ===\n")
    
    # Initialize database and create tables if they don't exist
    engine = create_engine(DATABASE_URI)
    Base.metadata.create_all(bind=engine)
    print("Database initialized and tables created.")
    
    # Check if there are any existing admin users
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        admin_count = session.query(UserModel).filter(UserModel.role == "admin").count()
        
        if admin_count > 0:
            print(f"There are already {admin_count} admin users in the database.")
            confirm = input("Do you want to create another admin? (y/n): ").lower()
            if confirm != 'y':
                print("Operation cancelled.")
                return
    except Exception as e:
        print(f"Error checking existing admins: {str(e)}")
        return
    finally:
        session.close()
    
    # Get user details
    username = input("Username: ")
    email = input("Email: ")
    
    # Get password with confirmation
    while True:
        password = getpass.getpass("Password (min 8 characters): ")
        
        if len(password) < 8:
            print("Password must be at least 8 characters.")
            continue
        
        confirm_password = getpass.getpass("Confirm password: ")
        
        if password != confirm_password:
            print("Passwords do not match.")
            continue
        
        break
    
    # Create the admin user
    create_admin_user(username, email, password)

if __name__ == "__main__":
    main() 