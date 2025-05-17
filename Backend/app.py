from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import auth
import users
import admin
import chatbot
import journal

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(chatbot.router)
app.include_router(journal.router)