from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router
from chatbot import router as chatbot_router
from journal import router as journal_router
from review import router as review_router
from users import router as users_router
from admin import router as admin_router
from therapist import router as therapist_router
from progress import router as progress_router
from database import Base, engine
from journal_database import JournalBase, journal_engine

# Create database tables
Base.metadata.create_all(bind=engine)
JournalBase.metadata.create_all(bind=journal_engine)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(auth_router)
app.include_router(chatbot_router)
app.include_router(journal_router)
app.include_router(review_router)
app.include_router(users_router)
app.include_router(admin_router)
app.include_router(therapist_router)
app.include_router(progress_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Mental Health Chatbot API"}