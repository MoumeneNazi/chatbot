from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from models import User
from database import SessionLocal
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
import logging
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

logging.basicConfig(level=logging.DEBUG)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, role: str):
    logging.debug(f"Creating access token with data: {data} and role: {role}")
    to_encode = data.copy()
    to_encode.update({"role": role})
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logging.debug(f"Generated token: {token}")
    return token

@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    logging.debug(f"Registering user: {user.username}")
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        logging.debug(f"Username {user.username} already registered.")
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_pw = pwd_context.hash(user.password)
    logging.debug(f"Hashed password for {user.username}: {hashed_pw}")
    new_user = User(username=user.username, hashed_password=hashed_pw, role="user")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = create_access_token({"sub": new_user.username}, new_user.role)
    logging.debug(f"User {user.username} registered successfully.")
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    logging.debug(f"Attempting login for user: {user.username}")
    db_user = db.query(User).filter(User.username == user.username).first()
    print(db_user)
    if not db_user:
        logging.debug(f"User {user.username} not found in database.")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not pwd_context.verify(user.password, db_user.hashed_password):
        logging.debug(f"Password verification failed for user: {user.username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    logging.debug(f"User {user.username} authenticated successfully.")
    token = create_access_token({"sub": db_user.username}, db_user.role)
    return {"access_token": token, "token_type": "bearer","role": db_user.role}

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    logging.debug(f"Authenticating token: {token}")
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            logging.debug("Token payload missing 'sub' field.")
            raise credentials_exception
        logging.debug(f"Token payload: {payload}")
    except JWTError as e:
        logging.debug(f"Token decoding failed: {e}")
        raise credentials_exception

    # Retrieve the user from the database
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        logging.debug(f"User {username} not found in database.")
        raise credentials_exception
    logging.debug(f"Authenticated user: {user.username}, Role: {user.role}")

    return user
def get_current_therapist(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Ensure the current user is a therapist."""
    user = get_current_user(token, db)
    if user.role != "therapist":
        logging.debug(f"Access denied for user: {user.username}, Role: {user.role}")
        raise HTTPException(status_code=403, detail="Access forbidden: Therapists only.")
    return user