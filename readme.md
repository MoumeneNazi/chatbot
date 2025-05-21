# 🧠 Mental Health Chatbot

A web-based mental health companion built with FastAPI, React, and SQLite databases.  
It offers therapeutic conversations, journaling, emotional tracking, and therapist access for user support and review.

---

## 🚀 Features

- 💬 Conversational chatbot using Groq API for natural language understanding
- 🧾 Secure journaling with sentiment analysis (separate database)
- 📊 Daily mood tracking and emotional trends
- 👤 User registration and authentication (JWT)
- 🧑‍⚕️ Therapist dashboard with access to user conversations
- 🌐 Public landing page with app info

---

## 🛠 Technologies

**Backend:**
- FastAPI
- SQLAlchemy (SQLite DB - users.db & journals.db)
- JWT for authentication
- Groq API for conversational capabilities
- TextBlob for sentiment analysis

**Frontend:**
- React (Create React App)
- React Router (multi-page support)
- Fetch API for backend integration
- Modern UI components

---

## ⚙️ Setup Instructions

### 🧩 Prerequisites

- Python 3.10+
- Node.js (for frontend)
- Virtual environment (recommended)

---

### 📦 Backend Setup

```bash
cd Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py  # Initialize database schemas
uvicorn app:app --reload
```

### 🖥️ Frontend Setup

```bash
cd frontend
npm install
npm start
```

---

## 📂 Project Structure

- **Backend/** - FastAPI backend services
  - `app.py` - Main application entry point
  - `database.py` - Main user database configuration
  - `journal_database.py` - Separate journal database configuration
  - Various router modules for different API endpoints

- **frontend/** - React frontend application
  - `src/` - Source code
  - `public/` - Static assets

---

## 🚀 Getting Started

1. Clone the repository
2. Set up backend (see Backend Setup)
3. Set up frontend (see Frontend Setup)
4. Visit http://localhost:3000 in your browser
5. Register a new account or login
6. Explore the chatbot, journaling, and other features

---

## 📄 License

MIT
