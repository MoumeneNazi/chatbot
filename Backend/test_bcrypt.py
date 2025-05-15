from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_password_hashing():
    password = "mimo\\"
    hashed_password = pwd_context.hash(password)
    print(f"Hashed password: {hashed_password}")

    # Verify the password
    is_valid = pwd_context.verify(password, hashed_password)
    print(f"Password verification result: {is_valid}")

if __name__ == "__main__":
    test_password_hashing()
