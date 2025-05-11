# 🧠 Mental Health Chatbot

A web-based mental health companion built with FastAPI, React, and Neo4j.  
It offers therapeutic conversations, journaling, emotional tracking, and therapist access for user support and review.

---

## 🚀 Features

- 💬 Conversational chatbot using NLP + symptom detection
- 🧾 Secure journaling with sentiment analysis
- 📊 Daily mood tracking and emotional trends
- 👤 User registration and authentication (JWT)
- 🧑‍⚕️ Therapist dashboard with access to user conversations
- 🌐 Public landing page with app info

---

## 🛠 Technologies

**Backend:**
- FastAPI
- SQLAlchemy (SQLite DB)
- Neo4j (symptom-disorder graph)
- JWT for auth
- TextBlob for sentiment analysis

**Frontend:**
- React (Create React App)
- React Router (multi-page support)
- Fetch API for backend integration

---

## ⚙️ Setup Instructions

### 🧩 Prerequisites

- Python 3.10+
- Node.js (for frontend)
- Neo4j (local or remote)
- Virtual environment (recommended)

---

### 📦 Backend Setup

```bash
cd Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
