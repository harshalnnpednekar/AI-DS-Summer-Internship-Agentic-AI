# OmniSync - Automated Academic Operations Platform

Welcome to **OmniSync**, a state-of-the-art unified platform meticulously engineered for academic institutions. Developed originally for the Artificial Intelligence & Data Science (AI & DS) department, OmniSync aims to revolutionize and automate conventional academic workflows. By integrating robust data extraction capabilities, intelligent attendance tracking, dynamic user interfaces, and automated background notifications, OmniSync empowers Head of Departments (HOD), Faculty members, and Students with a seamless digital experience.

## 🌟 Executive Summary

In the contemporary educational ecosystem, manual tracking of academic calendars and student attendance is both time-consuming and prone to human error. OmniSync bridges this gap by providing an end-to-end web-based solution that:
1. **Automates Academic Calendar Parsing**: Upload PDF calendars directly into the system, which leverages advanced extraction algorithms to parse events, categorize them by department and audience, and store them securely in the PostgreSQL database.
2. **Generates Defaulter Lists (with Advanced Granularity)**: Faculty can upload attendance sheets (CSV/Excel), and the system instantly analyzes the data. It now computes aggregate attendance statistics distinguishing between Theory, Practical, and Total attendance, seamlessly handling "N/A" edge cases for absent lab sessions.
3. **Proactive Notifications & Schedulers**: A robust background scheduling agent dispatches timely email alerts for upcoming events and attendance warnings to relevant students and faculty, ensuring no deadline is ever missed. It polls the database continuously without blocking the main event loop.
4. **Role-Based Access Control (RBAC)**: Segregated dashboards tailored specifically for HODs, Faculty, and Students, ensuring data privacy and operational security. Only authorized roles can broadcast emails or generate enterprise-grade reports.
5. **Ultra-Premium Enterprise Reporting**: Automatically generate and export "Academic Audit" quality PDF reports via jsPDF, complete with cover pages, standardized typography, automated pagination, custom coloring for critical cases, and formal signature blocks for HODs and Registrars.

---

## 🏗️ Architectural Overview

The OmniSync platform adopts a modern, decoupled client-server architecture to ensure high performance, scalability, and maintainability.

### Frontend Application
- **Framework**: React.js powered by Vite for lightning-fast Hot Module Replacement (HMR) and optimized production builds.
- **Styling**: Vanilla CSS combined with custom design tokens for a highly responsive, accessible, and aesthetically premium user interface. The UI features glassmorphism, dynamic grids, and refined spacing (like our custom sidebar layout).
- **Key Features**: Secure JWT-based authentication, interactive charts for attendance visualization, drag-and-drop file uploaders, real-time event polling, and client-side premium PDF generation.
- *For detailed frontend documentation, refer to the [Frontend Documentation](./frontend/README.md).*

### Backend Service
- **Framework**: FastAPI (Python 3.10+) for high-performance, asynchronous REST API endpoints.
- **Database**: PostgreSQL with SQLAlchemy (AsyncSession) for robust, ACID-compliant relational data management.
- **Task Scheduling**: APScheduler for asynchronous background tasks, specifically for periodic polling of upcoming events and automated email dispatching.
- **Authentication**: OAuth2 with Password Flow and JWT tokens (using python-jose and passlib).
- *For detailed backend documentation, refer to the [Backend Documentation](./backend/README.md).*

---

## 🚀 Key Capabilities & Modules

### 1. Smart Academic Calendar Management
The core component of OmniSync is its ability to digitize traditional PDF academic calendars. 
- **PDF Extraction**: Utilizing advanced text extraction techniques to identify tabular and listed data within complex PDF structures.
- **Intelligent Parsing**: Applies heuristic algorithms and regular expressions to extract dates, event titles, descriptions, and target audiences.
- **De-duplication Engine**: Automatically cross-references incoming events with existing database records to prevent redundant entries and maintain data hygiene.

### 2. Comprehensive Attendance Tracking & Analysis
Managing student attendance is simplified through an intuitive upload and processing pipeline.
- **Multi-format Support**: Accepts raw attendance data in both CSV and Excel formats.
- **Data Aggregation**: Merges data across multiple subjects (e.g., SE, TE, BE levels) to compute overall attendance percentages. We strictly distinguish between Theory and Practical attendances to give a highly accurate overview.
- **Edge-case Handling**: Accurately processes instances where practical attendance is "N/A", adjusting the denominator dynamically to prevent skewed percentages.
- **Defaulter Identification**: Automatically flags students whose cumulative attendance falls below the customizable departmental threshold (e.g., 75%), categorizing them into standard and "Critical" risk levels.
- **Dynamic Excel Generation**: Constructs fully formatted Master and Subject-specific Excel sheets dynamically in-memory and streams them directly to the client, removing any local filesystem clutter and ensuring data is always real-time.
- **Role-Based Defaulter Views**: Strictly enforces Role-Based Access Control (RBAC). Faculty members can securely view and manage defaulters strictly for the lectures they have conducted, while HODs maintain a panoramic view of all defaulters across the department.
- **Collapsible Accordion UI**: Attendance sheets and defaulter stats are intelligently grouped by Academic Year (FE, SE, TE, BE), Class, and Faculty, leveraging native HTML5 `<details>` for a clean, clutter-free dashboard experience that adapts intelligently based on the user's role.

### 3. Automated Notification Agent
OmniSync doesn't just store data; it actively works for you in the background.
- **Scheduled Polling**: An asynchronous scheduler checks the database every 5 minutes for upcoming events occurring within the next 7 days.
- **Email Delivery System**: Broadcasts customized HTML email notifications to registered users (using secure SMTP configuration).
- **Delivery Logging**: Maintains a precise audit trail (`send_logs` table) to monitor the success or failure of dispatched emails, with a configuration interface to manage and securely wipe logs when necessary.
- **Dynamic Configuration**: A dedicated UI allows adjusting defaulter thresholds, broadcast toggles, and UI preferences that instantly reflect and persist across user sessions.

### 4. Enterprise-Grade Export Engine
The UI contains a highly customized jsPDF integration.
- **Cover Pages**: Generates formal Academic Audit cover pages with institutional branding and matrix summaries.
- **Conditional Formatting**: Dynamically colors critical defaulter cases (in bold red) and standard defaulters (in amber) directly within the PDF tables.
- **Sign-off Workflows**: Automatically injects signature lines for authoritative validation by Head of Departments and the Academic Registrar.

---

## ⚙️ Environment Setup & Installation

To run OmniSync locally for development or evaluation purposes, follow the steps below.

### Prerequisites
- **Node.js** (v18.0.0 or higher)
- **Python** (v3.10 or higher)
- **PostgreSQL** (v14 or higher) running locally or via a Docker container.

### Step 1: Database Initialization
Ensure your PostgreSQL server is active. Create a new database to house the OmniSync data:
```sql
CREATE DATABASE event_notification_db;
```

### Step 2: Backend Configuration
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```
3. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run database migrations to construct the necessary tables:
   ```bash
   alembic upgrade head
   ```
5. Launch the FastAPI server:
   ```bash
   python run_backend.py
   ```
   *The API will be available at `http://127.0.0.1:8000`.*

### Step 3: Frontend Configuration
1. Open a new terminal session and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install the Node dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Access the web portal by navigating to `http://localhost:5173` in your preferred web browser.

---

## 📚 API Endpoints & Database Tables

The application relies on a comprehensive PostgreSQL database schema and RESTful API endpoints. For exhaustive details, refer to `backend/README.md`.

### Core Database Tables
- **Users & Profiles**: `users`, `faculty_profiles`, `student_profiles`
- **Academic Setup**: `classes`, `subjects`, `faculty_subject_mappings`
- **Attendance Tracking**: `attendances`, `lecture_attendances`, `defaulter_lists`
- **Events & Notifications**: `events`, `send_logs`

### Key API Domains
- **`/api/auth`**: User authentication, login, and registration.
- **`/api/events`**: Calendar parsing, event creation, and broadcast logs.
- **`/api/attendance`**: Lecture tracking, dashboard statistics, Excel generation, and defaulter generation (`/defaulters`, `/defaulters/broadcast`).
- **`/api/subjects`**: Academic subject management and faculty mapping.
- **`/api/users`**: User discovery and departmental filtering.

---

## 🛡️ Security & Access Control

OmniSync enforces strict security paradigms to protect sensitive academic data:
- **Password Hashing**: All user passwords are cryptographically hashed using the bcrypt algorithm before persistent storage.
- **Stateless Sessions**: Authentication is handled via stateless JSON Web Tokens (JWT), reducing server-side session overhead.
- **Role-Based Routing**: Both the frontend router and backend API endpoints enforce role checks. HODs and Faculty have elevated permissions for uploading data, while Students are restricted to read-only views of their own statistics.

---

*OmniSync — Bridging the gap between administration and automation.*