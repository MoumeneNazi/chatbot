from database import SessionLocal, UserModel

def check_users():
    db = SessionLocal()
    try:
        users = db.query(UserModel).all()
        if not users:
            print("No users found in database")
        else:
            print("Current users:")
            for user in users:
                print(f"Username: {user.username}, Role: {user.role}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users() 