import React from 'react';
import './Pages.css';

const PlaceholderPage = ({ title, subtitle }) => {
  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">{title}</h1>
        {subtitle && <p className="page-subtitle">{subtitle}</p>}
      </div>
      <div className="card flex-center" style={{ height: '300px', justifyContent: 'center' }}>
        <p className="text-secondary" style={{ fontSize: '1.25rem', fontWeight: 500 }}>
          {title} Interface Loading...
        </p>
      </div>
    </div>
  );
};

export const Dashboard = () => <PlaceholderPage title="Dashboard Overview" subtitle="Good morning, Dr. Priya 👋" />;
export const MarkAttendance = () => <PlaceholderPage title="Mark Lecture Attendance" subtitle="Submit attendance details for your lecture." />;
export const AttendanceData = () => <PlaceholderPage title="My Attendance Data" subtitle="Live data updated each time a faculty submits a lecture attendance record." />;
export const AcademicCalendar = () => <PlaceholderPage title="Academic Calendar & Automated Updates" subtitle="Upload the department PDF calendar. The agent parses it and broadcasts deadline alerts automatically." />;
