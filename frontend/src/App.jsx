import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import StudentDashboard from './pages/StudentDashboard';
import MarkAttendance from './pages/MarkAttendance';
import AttendanceTracking from './pages/AttendanceTracking';
import AcademicCalendar from './pages/AcademicCalendar';
import BroadcastLogs from './pages/BroadcastLogs';
import DefaulterManagement from './pages/DefaulterManagement';
import Reports from './pages/Reports';
import Configuration from './pages/Configuration';
import Profile from './pages/Profile';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Navigate to="/login" replace />} />
        
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/student-dashboard" element={<StudentDashboard />} />
          <Route path="/mark-attendance" element={<MarkAttendance />} />
          <Route path="/attendance-data" element={<AttendanceTracking />} />
          <Route path="/calendar" element={<AcademicCalendar />} />
          <Route path="/broadcast-logs" element={<BroadcastLogs />} />
          <Route path="/defaulter-management" element={<DefaulterManagement />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/configuration" element={<Configuration />} />
          <Route path="/profile" element={<Profile />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
