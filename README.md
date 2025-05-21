# Mental Health Chatbot Platform

A comprehensive mental health platform that combines AI-powered chat support with professional therapist oversight.

## Features

### For Users
- 🤖 AI-powered mental health chatbot
- 📝 Personal journal with sentiment analysis
- 📊 Progress tracking and mood monitoring
- 👥 Professional therapist reviews and insights
- 🔒 Secure and private conversations

### For Therapists
- 👥 Patient management dashboard
- 💬 Access to patient chat histories
- 📋 Review and insight publishing system
- 📊 Patient progress monitoring
- 🏥 Disorder-specific treatment tracking

## Technology Stack

### Backend
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- PostgreSQL (Database)
- Neo4j (Graph database for symptom-disorder relationships)
- JWT Authentication
- CORS middleware

### Frontend
- React.js
- React Router for navigation
- Axios for API communication
- Context API for state management
- Modern CSS with responsive design

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 14+
- PostgreSQL
- Neo4j (optional)

### Backend Setup
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

4. Initialize the database:
   ```bash
   python init_db.py
   ```

5. Run the backend server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

## API Documentation

### Authentication Endpoints
- POST `/api/auth/token` - Get access token
- POST `/api/auth/register` - Register new user

### Chat Endpoints
- GET `/api/chat/history` - Get user chat history
- POST `/api/chat` - Send message to chatbot
- GET `/api/chat/history/{user_id}` - Get specific user's chat (therapist only)
- POST `/api/chat/{user_id}` - Send message as therapist

### Journal Endpoints
- GET `/api/journal` - Get user's journal entries
- POST `/api/journal` - Create new journal entry
- GET `/api/journal/{user_id}` - Get user's journal (therapist only)

### Review Endpoints
- GET `/api/reviews` - Get reviews
- POST `/api/reviews` - Create review (therapist only)
- GET `/api/reviews/{user_id}` - Get user-specific reviews

### User Management
- GET `/api/admin/users` - Get user list (therapist only)
- PUT `/api/admin/promote/{username}` - Promote user to therapist

## Project Structure
See `structure.txt` for detailed project structure.

## Security Features
- JWT-based authentication
- Role-based access control
- Password hashing
- CORS protection
- Input validation
- SQL injection prevention

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
MIT License - see LICENSE file for details

## Administration

### Creating the First Admin User

To create the first admin user, run the following command:

```bash
cd Backend
python create_admin.py
```

Follow the prompts to create an admin username, email, and password. Once created, you can log in with these credentials and access the admin dashboard at `/admin/dashboard`.

As an admin, you can:
- Manage all user accounts (create, update roles, delete)
- Review and approve therapist applications
- Manage disorders and symptoms in the knowledge base
- Create other admin accounts 
