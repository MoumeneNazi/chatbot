#!/usr/bin/env python3
import sqlite3
import os
import sys
import getpass
from datetime import datetime
from passlib.context import CryptContext

# Password hashing 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def create_admin_user(username, password):
    try:
        # Connect to SQLite database
        conn = sqlite3.connect("mental_health.db")
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            print(f"Error: User '{username}' already exists.")
            return False
        
        # Hash the password
        hashed_password = get_password_hash(password)
        
        # Get current timestamp
        now = datetime.utcnow().isoformat()
        
        # Insert admin user
        cursor.execute(
            "INSERT INTO users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
            (username, hashed_password, "admin", now)
        )
        
        # Commit changes
        conn.commit()
        print(f"Admin user '{username}' created successfully!")
        return True
        
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        return False
        
    finally:
        if conn:
            conn.close()

def main():
    print("\n=== Create Admin User ===\n")
    
    # Get admin username
    username = input("Admin username: ")
    
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
    create_admin_user(username, password)

if __name__ == "__main__":
    main() 