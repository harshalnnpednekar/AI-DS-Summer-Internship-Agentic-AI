# OmniSync Backend Service

This directory contains the robust, asynchronous REST API that powers the OmniSync platform. Built on top of **FastAPI** and **PostgreSQL**, this backend is designed for high concurrency, strict data validation, and seamless background task execution.

## 🌟 Architectural Highlights

- **FastAPI Framework**: Chosen for its exceptional speed, built-in validation via Pydantic, and native support for asynchronous programming (ASGI).
- **SQLAlchemy 2.0 (Async)**: Utilizes asynchronous database sessions (`AsyncSession`) to ensure non-blocking database I/O, drastically improving throughput under heavy load.
- **Alembic Migrations**: Maintains a strict, version-controlled history of database schema changes, ensuring reproducible deployments across environments.
- **APScheduler**: Integrates the Advanced Python Scheduler to execute recurring background tasks—specifically, monitoring upcoming academic deadlines and dispatching email notifications.
- **Modular Routing**: API endpoints are logically segmented into routers (`users.py`, `events.py`, `attendance.py`, `auth.py`), adhering to Separation of Concerns (SoC).

## 🗂️ Directory Structure

```text
backend/
├── alembic/                # Database migration scripts and configuration
├── app/                    # Core application logic
│   ├── models.py           # SQLAlchemy ORM models (Database schema definitions)
│   ├── schemas.py          # Pydantic models (Data validation & serialization)
│   ├── crud.py             # Create, Read, Update, Delete (CRUD) operations
│   ├── database.py         # Database connection pooling and session management
│   ├── dependencies.py     # FastAPI dependencies (e.g., Auth, DB Session)
│   ├── main.py             # FastAPI application factory and lifecycle events
│   ├── routers/            # API Route definitions
│   └── services/           # Business logic and external integrations
│       ├── calendar_extractor/ # PDF parsing algorithms and utilities
│       ├── email/          # SMTP email dispatch services
│       └── scheduler/      # Background task orchestration
├── run_backend.py          # Uvicorn server entry point
├── alembic.ini             # Alembic configuration file
└── requirements.txt        # Python dependency manifest
```

## 🛠️ Core Services

### 1. Calendar Extractor (`app/services/calendar_extractor/`)
A specialized module tasked with parsing uploaded PDF academic calendars. 
- **`extractor.py`**: The main orchestrator that coordinates text extraction and validation.
- **`parser.py`**: Contains complex regular expressions and heuristic algorithms to isolate dates, event titles, and intended audiences from unstructured text.
- **`validator.py`**: Enforces strict Pydantic models (`AcademicEvent`) on the extracted data to ensure structural integrity before database insertion.

### 2. Automated Scheduler (`app/services/scheduler/`)
Operates independently of the HTTP request-response cycle to execute time-sensitive tasks.
- **`agent.py`**: Defines the `notification_workflow`, which queries the database for upcoming events (e.g., within 7 days) and prepares customized email templates.
- **`scheduler.py`**: Configures the `AsyncIOScheduler`, registering jobs to run at defined intervals (e.g., a CRON job executing every 5 minutes).

### 3. Authentication & Security
- Leverages OAuth2 Password Bearer flow.
- Passwords are hashed via the `passlib` library (bcrypt).
- JWTs are generated and validated using `python-jose`, ensuring secure, stateless API communication.

## 🗄️ Database Schema Reference

OmniSync utilizes a highly normalized PostgreSQL relational database. Below are the core tables and their structures as defined by our SQLAlchemy models.

### `users`
Core authentication table for all users (HOD, Faculty, Students).
| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | Primary Key | Unique user identifier |
| `email` | String(255) | Unique, Not Null | User's email address |
| `password_hash` | String(255) | Not Null | Bcrypt hashed password |
| `first_name` | String(100) | Not Null | User's first name |
| `last_name` | String(100) | Not Null | User's last name |
| `role` | Enum | Not Null | `HOD`, `FACULTY`, or `STUDENT` |
| `created_at` | DateTime | Not Null | Timestamp of creation |
| `updated_at` | DateTime | Not Null | Timestamp of last update |

### `faculty_profiles`
Extended profile information for Faculty members.
| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | Primary Key | Profile identifier |
| `user_id` | UUID | Foreign Key (`users.id`), Unique | Link to core user account |
| `department` | String(100) | Not Null | e.g., "AI & DS" |
| `designation` | String(100) | Not Null | e.g., "Assistant Professor" |
| `assigned_classes` | String(100) | Nullable | Classes assigned (e.g., "SE-A") |

### `student_profiles`
Extended profile information for Students.
| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | Primary Key | Profile identifier |
| `user_id` | UUID | Foreign Key (`users.id`), Unique | Link to core user account |
| `roll_number` | String(50) | Unique, Not Null | Unique student roll number |
| `department` | String(100) | Not Null | e.g., "AI & DS" |
| `current_semester` | String(20) | Not Null | e.g., "Semester 5" |
| `division` | String(50) | Not Null | e.g., "TE-A" |

### `events`
Parsed events extracted from the Academic Calendar.
| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `event_id` | UUID | Primary Key | Unique event identifier |
| `title` | String(200) | Not Null | Event name/title |
| `description` | String(2000)| Nullable | Detailed event description |
| `event_date` | Date | Not Null | Date of the event |
| `department` | String(100) | Not Null | Target department |
| `audience` | String(50) | Not Null | e.g., "SE", "TE", "BE", or "ALL" |

### `send_logs`
Audit trail for background email dispatching.
| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `log_id` | UUID | Primary Key | Log identifier |
| `event_id` | UUID | Foreign Key (`events.event_id`) | Associated event |
| `student_email` | String(255) | Not Null | Recipient email address |
| `status` | String(50) | Not Null | e.g., "SENT", "FAILED" |
| `timestamp` | DateTime | Not Null | Dispatch timestamp |

### `attendances`
Raw parsed attendance records mapped to students.
| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | Primary Key | Attendance record identifier |
| `date` | Date | Not Null | Date of attendance |
| `subject` | String(100) | Not Null | Subject name |
| `faculty_id` | UUID | Foreign Key (`users.id`) | Faculty who submitted |
| `division` | String(50) | Not Null | Class division |
| `status` | JSONB | Not Null | JSON Map: `student_id` -> "Present"/"Absent" |

### `defaulter_lists`
Generated lists of students who fall below the minimum attendance threshold.
| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | Primary Key | List identifier |
| `generated_by`| UUID | Foreign Key (`users.id`) | Faculty/HOD who generated |
| `division` | String(50) | Not Null | Class division |
| `month` | String(20) | Not Null | Month of reference |
| `generated_at`| DateTime | Not Null | Generation timestamp |
| `student_ids` | JSONB | Not Null | Array of defaulter UUIDs |
| `broadcast_status`| String(20) | Not Null, Default: "PENDING" | Status of warning emails |

### `classes` & `subjects`
Normalization tables for academic structures.
- **`classes`**: `id` (UUID), `name` (String 50), `department_id` (String 100), `total_students` (Integer)
- **`subjects`**: `id` (UUID), `code` (String 50), `name` (String 100), `department_id` (String 100)

### `faculty_subject_mappings`
Maps which faculty teaches which subject in which class.
| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | Primary Key | Mapping identifier |
| `faculty_id` | UUID | Foreign Key (`users.id`) | Assigned Faculty |
| `class_id` | UUID | Foreign Key (`classes.id`) | Target Class |
| `subject_id` | UUID | Foreign Key (`subjects.id`)| Assigned Subject |

### `lecture_attendances`
Tracks per-lecture stats, topics covered, and specific absentees.
| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | Primary Key | Session identifier |
| `faculty_id` | UUID | Foreign Key (`users.id`) | Executing Faculty |
| `class_id` | UUID | Foreign Key (`classes.id`) | Executing Class |
| `subject_id` | UUID | Foreign Key (`subjects.id`)| Topic Subject |
| `lecture_date`| Date | Not Null | Date of session |
| `topic_covered`| String(200) | Not Null | Lesson summary |
| `total_students_enrolled` | Integer | Not Null | Class capacity |
| `students_present_count` | Integer | Not Null | Number of attendees |
| `absentee_roll_numbers` | JSONB | Nullable | Array of absent roll numbers |
| `session_type`| String(20) | Not Null, Default: "Lecture"| e.g., "Lecture", "Practical" |
| `created_at` | DateTime | Not Null | Entry creation timestamp |

## 🌐 API Endpoints Reference

The backend exposes a comprehensive set of RESTful endpoints prefixed with `/api`. Most endpoints require a valid Bearer JWT token in the `Authorization` header.

### Authentication (`/api/auth`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/login` | Authenticates user and returns JWT access token | No |
| `POST` | `/signup` | Registers a new HOD, Faculty, or Student | No |
| `POST` | `/logout` | Invalidates the current session | Yes |
| `GET`  | `/me` | Returns the profile of the currently authenticated user | Yes |
| `POST` | `/repair-profile`| Utility endpoint to fix corrupted user profiles | Yes |

### Events & Calendar (`/api/events`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET`  | `/upcoming` | Retrieves events happening within a specified timeframe (e.g., next 7 days) | No |
| `GET`  | `/events` | Retrieves a paginated list of all events | No |
| `POST` | `/` | Manually creates a new event | Yes (HOD/Faculty) |
| `POST` | `/extract` | Parses an uploaded Academic Calendar PDF and extracts events | Yes (HOD/Faculty) |
| `POST` | `/send-log` | Records an audit log when an automated email is dispatched | System/Internal |
| `GET`  | `/broadcast-logs` | Retrieves broadcast delivery logs (simulated or actual) | Yes |
| `DELETE` | `/broadcast-logs` | Clears all broadcast logs from the database | Yes |

### Attendance (`/api/attendance`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET`  | `/form-meta` | Fetches metadata (subjects, classes) for the attendance upload form | Yes (Faculty) |
| `POST` | `/submit` | Accepts CSV/Excel files to bulk upload attendance records | Yes (Faculty) |
| `GET`  | `/stats` | Retrieves aggregated attendance statistics for dashboard charts | Yes |
| `POST` | `/generate` | Generates a defaulter list based on a minimum threshold (e.g., 75%) | Yes (HOD/Faculty) |
| `POST` | `/broadcast/{list_id}`| Dispatches warning emails to all students on a specific defaulter list | Yes (HOD/Faculty) |

### Users & Profiles (`/api/users`)
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET`  | `/` | Retrieves a list of users (primarily used for fetching students) | Yes (Faculty) |
| `GET`  | `/department/{department}` | Retrieves all users belonging to a specific department | Yes (HOD) |

## 🚀 Getting Started

### 1. Environment Preparation
Ensure Python 3.10+ is installed. Create an isolated virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Database Initialization
Ensure PostgreSQL is running and a database named `event_notification_db` exists. The connection string is managed in `app/database.py`.

Run the Alembic migrations to construct the schema:
```bash
alembic upgrade head
```

### 3. Running the Server
Launch the development server using the provided runner script:
```bash
python run_backend.py
```
This script invokes `uvicorn` with hot-reloading enabled. The API will be accessible at `http://127.0.0.1:8000`.

### 4. Interactive API Documentation
FastAPI automatically generates interactive documentation for all endpoints. Once the server is running, visit:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

Use these interfaces to explore the API schema, test endpoints, and verify authentication flows directly from your browser.
