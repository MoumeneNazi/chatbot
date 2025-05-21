import sqlite3
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Add is_active column to users table and set all existing accounts to active."""
    try:
        # Create the database directory if it doesn't exist
        DB_DIR = os.path.dirname(os.path.abspath(__file__))
        DB_FILE = os.path.join(DB_DIR, "users.db")
        
        # Connect to the database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if is_active column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'is_active' not in column_names:
            logger.info("Adding is_active column to users table...")
            
            # Add the is_active column with default value of TRUE (1)
            cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")
            conn.commit()
            
            # Get number of updated rows
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            logger.info(f"Migration successful: Added is_active column to {user_count} users")
        else:
            logger.info("is_active column already exists in users table")
        
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    run_migration() 