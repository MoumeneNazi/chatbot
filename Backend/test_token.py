from jose import jwt
from datetime import datetime, timedelta
from config import SECRET_KEY, ALGORITHM

def create_test_token(username: str):
    expire = datetime.utcnow() + timedelta(minutes=30)
    payload = {"sub": username, "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print(f"Generated token: {token}")
    return token

def validate_test_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded token: {payload}")
    except Exception as e:
        print(f"Token validation failed: {e}")

if __name__ == "__main__":
    username = "test_user"
    token = create_test_token(username)
    validate_test_token(token)
