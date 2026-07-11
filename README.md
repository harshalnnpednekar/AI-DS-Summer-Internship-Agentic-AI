# AI-DS-Summer-Internship-Agentic-AI

A unified platform for automated attendance tracking, academic calendar management, and defaulter list generation — built for the AI & DS faculty. This system is known as **OmniSync**.

## Project Structure

- `frontend/` - React-based user interface for the OmniSync Portal, featuring Role-Based Access Control (HOD, Faculty, Student).
- `backend/` - FastAPI backend application handling authentication, data storage, and business logic.
- `AcademicCalendarExtractor/` - Automated parsing and extraction tool for Academic Calendars.

## Setup Instructions

### 1. Database Setup
Ensure you have PostgreSQL installed. Create a database named `event_notification_db`.

### 2. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the database migrations to set up the schema:
   ```bash
   python -m alembic upgrade head
   ```
5. Start the backend server:
   ```bash
   python run_backend.py
   ```
   *The backend will run on `http://127.0.0.1:8000`.*

### 3. Frontend Setup
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install the dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Open the application in your browser at `http://localhost:5173`. You can sign up for a new account or use one of the demo configurations.

*For more details, please refer to [backend/README.md](backend/README.md) and [frontend/README.md](frontend/README.md).*