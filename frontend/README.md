# OmniSync Portal — Frontend

This is the React-based frontend application for the VESIT AI & Data Science OmniSync Platform. It provides a unified, premium-grade enterprise interface for faculty members to manage attendance, track academic calendars, and generate defaulter lists automatically.

## Features

- **Role-Based Dashboards**: Distinct experiences for **HODs** (department-wide overview of all faculty attendance data) and **Faculty** (individual stats and class management).
- **Attendance Management**: Mark daily lecture attendance with support for both **Theory** and **Practical** sessions. Track historical data with visual progress indicators.
- **Defaulter Management**: Automated generation and broadcasting of defaulter lists based on customizable thresholds.
- **Academic Calendar**: Visual timeline of critical upcoming deadlines parsed by the backend agent.
- **Reports & Exports**: Secure hub for downloading official PDF, XLSX, and CSV reports.

## Technology Stack

- **React 18**
- **Vite**
- **React Router v6**
- **Lucide Icons**
- **Vanilla CSS** (Custom Design System with CSS Variables)

## Setup Instructions

### Prerequisites
- Node.js (v18 or higher recommended)
- npm

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd frontend
   ```

2. **Install the required dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Access the application:**
   Open your browser and navigate to `http://localhost:5173`. 
   
   *Note: The frontend is now fully connected to the backend API via proxy configured in Vite. You must have the backend server running on `localhost:8000` to handle authentication (Sign Up / Log In) and data loading successfully.*
