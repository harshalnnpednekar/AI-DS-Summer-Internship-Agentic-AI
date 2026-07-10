import React from 'react';
import { TrendingUp, BookOpen, AlertTriangle, Search } from 'lucide-react';
import './Pages.css';
import './AttendanceTracking.css';

const AttendanceTracking = () => {
  return (
    <div className="page-container">
      <div className="page-header">

        <h1 className="page-title">My Attendance Data</h1>
        <p className="page-subtitle">Live data updated each time a faculty submits a lecture attendance record.</p>
      </div>

      <div className="tracking-stats-grid">
        <div className="card stat-card">
          <div className="stat-header">
            <h3>MY AVG. ATTENDANCE</h3>
            <div className="stat-icon bg-success-light text-success">
              <TrendingUp size={18} />
            </div>
          </div>
          <div className="stat-value">88%</div>
          <div className="stat-context">Across tracked lectures</div>
        </div>

        <div className="card stat-card">
          <div className="stat-header">
            <h3>TOTAL LECTURES CONDUCTED</h3>
            <div className="stat-icon bg-secondary-light text-secondary">
              <BookOpen size={18} />
            </div>
          </div>
          <div className="stat-value">42</div>
          <div className="stat-context">Current academic semester</div>
        </div>
        
        <div className="card stat-card">
          <div className="stat-header">
            <h3>UNDER 75% THRESHOLD</h3>
            <div className="stat-icon" style={{ backgroundColor: 'var(--color-danger-bg)', color: 'var(--color-danger)' }}>
              <AlertTriangle size={18} />
            </div>
          </div>
          <div className="stat-value">0</div>
          <div className="stat-context">Class-subject pairs at risk</div>
        </div>
      </div>

      <div className="card table-card">
        <div className="table-header-toolbar">
          <div className="toolbar-title">
            <UsersIcon />
            <h2>Class-wise Attendance Summary</h2>
          </div>
          <div className="toolbar-actions">
            <div className="search-box">
              <Search size={16} className="text-secondary" />
              <input type="text" placeholder="Search..." className="search-input" />
            </div>
            <select className="filter-select">
              <option value="All">All</option>
              <option value="SE">SE</option>
              <option value="TE">TE</option>
            </select>
          </div>
        </div>

        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>CLASS</th>
                <th>SUBJECT</th>
                <th>PROFESSOR</th>
                <th>LECTURES</th>
                <th>ATTENDANCE</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><span className="class-badge">SE-A</span></td>
                <td className="font-medium">Data Structures & Algorithms</td>
                <td>Dr. Priya Mehta</td>
                <td>42</td>
                <td>
                  <div className="attendance-progress-cell">
                    <div className="attendance-progress-bg">
                      <div className="attendance-progress-fill" style={{ width: '88%', backgroundColor: 'var(--color-success)' }}></div>
                    </div>
                    <span className="font-semibold text-success">88%</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div className="table-footer flex-between">
          <span>Showing 1 of 1 records</span>
          <div className="legend-container">
            <div className="legend-item"><span className="legend-dot bg-success"></span> &gt;75% Compliant</div>
            <div className="legend-item"><span className="legend-dot bg-warning"></span> 60-75% At Risk</div>
            <div className="legend-item"><span className="legend-dot bg-danger"></span> &lt;60% Critical</div>
          </div>
        </div>
      </div>
    </div>
  );
};

const UsersIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-secondary mr-2">
    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path>
    <circle cx="9" cy="7" r="4"></circle>
    <path d="M22 21v-2a4 4 0 0 0-3-3.87"></path>
    <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
  </svg>
);

export default AttendanceTracking;
