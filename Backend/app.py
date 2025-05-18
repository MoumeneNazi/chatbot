from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from auth import router as auth_router
from chatbot import router as chatbot_router
from chat import router as chat_router
from journal import router as journal_router
from review import router as review_router
from users import router as users_router
from admin import router as admin_router
from therapist import router as therapist_router
from progress import router as progress_router
from database import Base, engine
from journal_database import JournalBase, journal_engine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Add custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for validation errors to ensure they're formatted as strings
    and don't cause rendering issues in the frontend.
    """
    logger.error(f"Validation error: {exc.errors()}")
    
    # Format validation errors as a readable string
    error_messages = []
    for error in exc.errors():
        location = " -> ".join(str(loc) for loc in error["loc"])
        message = f"{location}: {error['msg']}"
        error_messages.append(message)
    
    return JSONResponse(
        status_code=422,
        content={"detail": "; ".join(error_messages)}
    )

# Include routers
app.include_router(auth_router)
app.include_router(chat_router)
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