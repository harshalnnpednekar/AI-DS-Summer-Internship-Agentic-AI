# EduAgent — College Event Notification System (Backend)

> A FastAPI-based REST API backend for managing college events, student records, and email notification delivery logs. Built as part of a summer internship project, this system is designed to be integrated with an automated scheduler and email notification agent.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Docker Setup for PostgreSQL](#docker-setup-for-postgresql)
- [Environment Variables](#environment-variables)
- [Database Migrations (Alembic)](#database-migrations-alembic)
- [Seeding Sample Data](#seeding-sample-data)
- [Running the Server](#running-the-server)
- [Swagger / API Documentation](#swagger--api-documentation)
- [API Endpoints](#api-endpoints)
- [Example curl Commands](#example-curl-commands)
- [Testing with Postman](#testing-with-postman)
- [Integration Notes](#integration-notes)
- [Future Improvements](#future-improvements)

---

## Project Overview

The **EduAgent Backend** is the data and API layer for a college event notification system. It exposes REST endpoints to:

- Manage upcoming college events (exams, deadlines, guest lectures, etc.)
- Store student records by department
- Log the status of email notifications sent to students

This backend is designed to be consumed by an **AI scheduling agent** (EduAgent) that automatically queries upcoming events and dispatches email notifications to the relevant students.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | [FastAPI](https://fastapi.tiangolo.com/) `>= 0.111.0` |
| ASGI Server | [Uvicorn](https://www.uvicorn.org/) `>= 0.29.0` |
| ORM | [SQLAlchemy 2.x](https://docs.sqlalchemy.org/) (async) `>= 2.0.35` |
| Database | [PostgreSQL](https://www.postgresql.org/) (via Docker) |
| DB Driver | [Psycopg v3](https://www.psycopg.org/psycopg3/) (binary) `>= 3.x` |
| Migrations | [Alembic](https://alembic.sqlalchemy.org/) `>= 1.13.2` |
| Validation | [Pydantic v2](https://docs.pydantic.dev/latest/) `>= 2.7.1` |
| Config | [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) `>= 2.2.1` |
| Data Seeding | Custom async seed script |
| Language | Python 3.11+ |

---

## Project Structure

```
backend/
├── .env                        # Local environment variables (not committed)
├── .env.example                # Template for environment variables
├── alembic.ini                 # Alembic configuration
├── requirements.txt            # Python dependencies
│
├── alembic/
│   ├── env.py                  # Alembic migration environment (imports models)
│   ├── script.py.mako          # Migration file template
│   └── versions/               # Auto-generated migration files
│       └── xxxxxx_initial_tables.py
│
└── app/
    ├── config.py               # Pydantic settings (reads from .env)
    ├── database.py             # Async SQLAlchemy engine, session, Base
    ├── models.py               # SQLAlchemy ORM models (Event, Student, SendLog)
    ├── schemas.py              # Pydantic request/response schemas
    ├── crud.py                 # Async CRUD operations
    ├── seed.py                 # Script to populate initial test data
    ├── main.py                 # FastAPI app entry point, middleware, routers
    │
    └── routers/
        ├── __init__.py
        ├── events.py           # GET /events/upcoming, POST /events
        ├── students.py         # GET /students
        └── logs.py             # POST /send-log
```

---

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** — [Download](https://www.python.org/downloads/)
- **Docker Desktop** — [Download](https://www.docker.com/products/docker-desktop/) (for PostgreSQL)
- **pip** — comes bundled with Python

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd backend
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Database and Migrations

Ensure your PostgreSQL instance is running. Then run:
```bash
python -m alembic upgrade head
```

---

## Docker Setup for PostgreSQL

This project uses a PostgreSQL database running in Docker. Run the following command to start a container:

```bash
docker run -d \
  --name eduagent-pg \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=event_notification \
  -p 5432:5432 \
  postgres:15
```

To verify the container is running:

```bash
docker ps
```

To connect to the database directly:

```bash
docker exec -it eduagent-pg psql -U postgres -d event_notification
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

### `.env.example`

```env
DATABASE_URL=
APP_NAME=
DEBUG=
```

### `.env` (example values)

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/event_notification
APP_NAME=EduAgent
DEBUG=True
```

> **Note:** The `DATABASE_URL` must use the `postgresql+psycopg://` scheme (Psycopg v3 async driver). Do not use `postgresql://` directly.

All settings are loaded via `pydantic-settings` in [`app/config.py`](app/config.py) and are available throughout the app via:

```python
from app.config import settings
settings.DATABASE_URL
```

---

## Database Migrations (Alembic)

Alembic handles schema migrations. The `alembic/env.py` is configured to auto-detect your models.

### Generate a new migration

Run this from the `backend/` directory (with your virtual environment activated):

```bash
alembic revision --autogenerate -m "initial tables"
```

### Apply migrations to the database

```bash
alembic upgrade head
```

### Verify tables were created

```bash
docker exec -it eduagent-pg psql -U postgres -d event_notification -c "\dt"
```

Expected output:

```
          List of relations
 Schema |    Name    | Type  |  Owner
--------+------------+-------+----------
 public | events     | table | postgres
 public | send_logs  | table | postgres
 public | students   | table | postgres
```

### Rollback last migration

```bash
alembic downgrade -1
```

---

## Seeding Sample Data

The seed script inserts test students and upcoming events into the database. It checks for duplicates before inserting.

```bash
python app/seed.py
```

### What gets seeded

**Students** (Department: AIDS):

| Name    | Email                           |
|---------|---------------------------------|
| Member1 | puneetdhongade26@gmail.com      |
| Member2 | puneetsdhongade2006@gmail.com   |

**Events** (relative to current date):

| Title                          | Days from now |
|-------------------------------|---------------|
| Unit Test 1                   | +2 days       |
| Assignment Submission Deadline | +4 days       |
| Guest Lecture — AI in Industry | +7 days       |

> **Windows Note:** The seed script uses `SelectorEventLoop` for Windows compatibility with Psycopg v3 (avoids the ProactorEventLoop error).

---

## Running the Server

Start the development server using the provided run script (handles Windows compatibility automatically):

```bash
python run_backend.py
```

The server will start at: **http://127.0.0.1:8000**

---

## Swagger / API Documentation

FastAPI automatically generates interactive API documentation.

| Documentation | URL |
|---|---|
| Swagger UI (interactive) | http://127.0.0.1:8000/docs |
| ReDoc (read-only) | http://127.0.0.1:8000/redoc |
| OpenAPI JSON schema | http://127.0.0.1:8000/openapi.json |

---

## API Endpoints

### `GET /` — Health Check

Returns the API status.

**Response `200 OK`:**
```json
{
  "status": "ok",
  "message": "EduAgent API is running"
}
```

---

### `GET /events/upcoming` — Upcoming Events

Returns events happening within the next N days.

**Query Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `days` | integer | `2` | Number of days ahead to search |

**Response `200 OK`:**
```json
[
  {
    "event_id": "a1b2c3d4-...",
    "title": "Unit Test 1",
    "description": "First unit test covering units 1 and 2",
    "event_date": "2026-07-06",
    "department": "AIDS",
    "audience": "ALL"
  }
]
```

---

### `POST /events` — Create Event(s)

Creates a single event or a bulk list of events.

**Request Body (single event):**
```json
{
  "title": "Mid Semester Exam",
  "description": "Covers topics from Unit 1 to Unit 3",
  "event_date": "2026-07-10",
  "department": "AIDS",
  "audience": "ALL"
}
```

**Request Body (bulk list):**
```json
[
  {
    "title": "Event A",
    "description": "Description A",
    "event_date": "2026-07-10",
    "department": "AIDS",
    "audience": "ALL"
  },
  {
    "title": "Event B",
    "description": "Description B",
    "event_date": "2026-07-11",
    "department": "AIDS",
    "audience": "students"
  }
]
```

**Valid `audience` values:** `students`, `faculty`, `staff`, `public`, `ALL`

**Response `201 Created`:**
```json
{
  "event_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Mid Semester Exam",
  "description": "Covers topics from Unit 1 to Unit 3",
  "event_date": "2026-07-10",
  "department": "AIDS",
  "audience": "ALL"
}
```

---

### `GET /students` — List Students

Returns all students, optionally filtered by department.

**Query Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `department` | string | `ALL` | Department name or `ALL` for all departments |

**Response `200 OK`:**
```json
[
  {
    "student_id": "b2c3d4e5-...",
    "name": "Member1",
    "email": "puneetdhongade26@gmail.com",
    "department": "AIDS"
  },
  {
    "student_id": "c3d4e5f6-...",
    "name": "Member2",
    "email": "puneetsdhongade2006@gmail.com",
    "department": "AIDS"
  }
]
```

---

### `POST /send-log` — Log Email Delivery

Stores an email notification delivery log for a specific event and student.

**Request Body:**
```json
{
  "event_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "student_email": "puneetdhongade26@gmail.com",
  "status": "sent"
}
```

**Valid `status` values:** `sent`, `failed`

**Response `201 Created`:**
```json
{
  "log_id": "d4e5f6a7-...",
  "event_id": "a1b2c3d4-...",
  "student_email": "puneetdhongade26@gmail.com",
  "status": "sent",
  "timestamp": "2026-07-04T14:00:00.000000+05:30"
}
```

---

## Example curl Commands

### Health Check

```bash
curl http://127.0.0.1:8000/
```

### Get upcoming events (next 2 days)

```bash
curl "http://127.0.0.1:8000/events/upcoming?days=2"
```

### Create a single event

```bash
curl -X POST http://127.0.0.1:8000/events \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mid Semester Exam",
    "description": "Covers Unit 1 to 3",
    "event_date": "2026-07-10",
    "department": "AIDS",
    "audience": "ALL"
  }'
```

### Get all students in AIDS department

```bash
curl "http://127.0.0.1:8000/students?department=AIDS"
```

### Log a sent email notification

```bash
curl -X POST http://127.0.0.1:8000/send-log \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "student_email": "puneetdhongade26@gmail.com",
    "status": "sent"
  }'
```

---

## Testing with Postman

### Import and setup

1. Open [Postman](https://www.postman.com/).
2. Click **Import** → **Link** and enter: `http://127.0.0.1:8000/openapi.json`
3. Postman will automatically generate a collection from the OpenAPI schema.

### Recommended test order

1. `GET /` — verify server is running
2. `POST /events` — create a test event, copy the `event_id` from the response
3. `GET /events/upcoming?days=7` — verify the created event appears
4. `GET /students?department=AIDS` — verify seed students are present
5. `POST /send-log` — use the `event_id` from step 2

### Setting a base URL variable

In Postman, create an **environment variable**:

| Variable | Value |
|---|---|
| `BASE_URL` | `http://127.0.0.1:8000` |

Then use `{{BASE_URL}}/events/upcoming` in your requests.

---

## Integration Notes

### Scheduler Integration

The EduAgent scheduler (a separate service/script) should:

1. Call `GET /events/upcoming?days=N` at regular intervals (e.g., daily at 8:00 AM).
2. For each event returned, call `GET /students?department=<event.department>` to get the target audience.
3. Send notification emails to each student.
4. After each email attempt, call `POST /send-log` to record the delivery status (`sent` or `failed`).

### Email Service Integration

The backend does **not** send emails directly. It acts purely as a data store. Your email agent/service should:

- Read recipients from `GET /students`
- Read event details from `GET /events/upcoming`
- Write delivery results to `POST /send-log`

This separation allows you to swap or upgrade the email service without modifying the backend.

### CORS

The backend allows all origins (`*`) by default. For production, restrict this to your frontend/agent domain in `app/config.py`:

```python
ALLOWED_ORIGINS: list[str] = ["https://your-frontend.com"]
```

---

## Future Improvements

| Area | Improvement |
|---|---|
| Authentication | Add JWT-based auth for admin endpoints |
| Event Management | Add `GET /events/{id}`, `PUT /events/{id}`, `DELETE /events/{id}` |
| Student Management | Add `POST /students`, `PUT /students/{id}`, `DELETE /students/{id}` |
| Filtering | Add date range filters to `GET /events/upcoming` |
| Pagination | Add `limit` and `offset` query parameters for large datasets |
| Notification Status | Add `GET /send-log?event_id=...` to query delivery history |
| Background Tasks | Use FastAPI `BackgroundTasks` or Celery for async email dispatch |
| Production Config | Add `.env.production` with proper secret management |
| Testing | Add `pytest` + `httpx` integration tests for all endpoints |
| Logging | Persist structured logs (JSON) to file or external log service |
| Docker Compose | Add `docker-compose.yml` to run both API and DB together |
| Deployment | Add `Dockerfile` for containerized API deployment |

---

## License

This project is developed as part of a college summer internship program.

---

> Made with ❤️ for EduAgent — College Event Notification System
