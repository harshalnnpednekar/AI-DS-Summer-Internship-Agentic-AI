import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import MarkAttendance from './pages/MarkAttendance';
import AttendanceTracking from './pages/AttendanceTracking';
import AcademicCalendar from './pages/AcademicCalendar';
import BroadcastLogs from './pages/BroadcastLogs';
import DefaulterManagement from './pages/DefaulterManagement';
import Reports from './pages/Reports';
import Configuration from './pages/Configuration';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="mark-attendance" element={<MarkAttendance />} />
          <Route path="attendance-data" element={<AttendanceTracking />} />
          <Route path="calendar" element={<AcademicCalendar />} />
          <Route path="broadcast-logs" element={<BroadcastLogs />} />
          <Route path="defaulter-management" element={<DefaulterManagement />} />
          <Route path="reports" element={<Reports />} />
          <Route path="configuration" element={<Configuration />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
