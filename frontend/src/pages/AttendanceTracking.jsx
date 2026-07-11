import React, { useState, useEffect } from 'react';
import { TrendingUp, BookOpen, AlertTriangle, Search } from 'lucide-react';
import './Pages.css';
import './AttendanceTracking.css';

const AttendanceTracking = () => {
  const [stats, setStats] = useState({ 
    total_lectures: 0, 
    avg_attendance: 0, 
    under_75_count: 0,
    class_wise_stats: [] 
  });
  const [filter, setFilter] = useState('All');
  const [search, setSearch] = useState('');
  
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const token = localStorage.getItem('accessToken');
        const response = await fetch(`/api/attendance/stats?t=${Date.now()}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        if (data.success) {
          setStats(data.data);
        }
      } catch (err) {
        console.error("Failed to fetch tracking stats", err);
      }
    };
    fetchStats();
  }, []);

  const filteredStats = (stats.class_wise_stats || []).filter(stat => {
    const matchesFilter = filter === 'All' || stat.class.startsWith(filter);
    const matchesSearch = stat.class.toLowerCase().includes(search.toLowerCase()) || 
                          stat.subject.toLowerCase().includes(search.toLowerCase());
    return matchesFilter && matchesSearch;
  });
  return (
    <div className="page-container">
      <div className="page-header">

        <h1 className="page-title">Attendance Data</h1>
        <p className="page-subtitle">Live data updated each time a faculty submits a lecture attendance record.</p>
      </div>

      <div className="tracking-stats-grid">
        <div className="card stat-card">
          <div className="stat-header">
            <h3>AVG. ATTENDANCE</h3>
            <div className="stat-icon bg-success-light text-success">
              <TrendingUp size={18} />
            </div>
          </div>
          <div className="stat-value">{stats.avg_attendance}%</div>
          <div className="stat-context">Across tracked lectures</div>
        </div>

        <div className="card stat-card">
          <div className="stat-header">
            <h3>TOTAL LECTURES CONDUCTED</h3>
            <div className="stat-icon bg-secondary-light text-secondary">
              <BookOpen size={18} />
            </div>
          </div>
          <div className="stat-value">{stats.total_lectures}</div>
          <div className="stat-context">Current academic semester</div>
        </div>
        
        <div className="card stat-card">
          <div className="stat-header">
            <h3>UNDER 75% THRESHOLD</h3>
            <div className="stat-icon" style={{ backgroundColor: 'var(--color-danger-bg)', color: 'var(--color-danger)' }}>
              <AlertTriangle size={18} />
            </div>
          </div>
          <div className="stat-value">{stats.under_75_count}</div>
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
              <input type="text" placeholder="Search..." className="search-input" value={search} onChange={(e) => setSearch(e.target.value)} />
            </div>
            <select className="filter-select" value={filter} onChange={(e) => setFilter(e.target.value)}>
              <option value="All">All</option>
              <option value="FE">FE</option>
              <option value="SE">SE</option>
              <option value="TE">TE</option>
              <option value="BE">BE</option>
            </select>
          </div>
        </div>

        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th style={{textAlign: 'center'}}>CLASS</th>
                <th style={{textAlign: 'center'}}>SUBJECT</th>
                <th style={{textAlign: 'center'}}>TYPE</th>
                <th style={{textAlign: 'center'}}>PROFESSOR</th>
                <th style={{textAlign: 'center'}}>LECTURES</th>
                <th style={{textAlign: 'center'}}>ATTENDANCE</th>
              </tr>
            </thead>
            <tbody>
              {filteredStats.map((stat, idx) => (
                <tr key={idx}>
                  <td style={{textAlign: 'center'}}><span className="class-badge">{stat.class}</span></td>
                  <td className="font-medium" style={{textAlign: 'center'}}>{stat.subject}</td>
                  <td style={{textAlign: 'center'}}>{stat.session_type === 'Lecture' ? 'Theory' : stat.session_type === 'Lab' ? 'Practical' : stat.session_type || 'Theory'}</td>
                  <td style={{textAlign: 'center'}}>{stat.professor}</td>
                  <td style={{textAlign: 'center'}}>{stat.lectures}</td>
                  <td>
                    <div className="attendance-progress-cell" style={{justifyContent: 'center'}}>
                      <div className="attendance-progress-bg">
                        <div className="attendance-progress-fill" style={{ width: stat.attendance, backgroundColor: stat.attendance_num >= 75 ? 'var(--color-success)' : stat.attendance_num >= 60 ? 'var(--color-warning)' : 'var(--color-danger)' }}></div>
                      </div>
                      <span className={`font-semibold ${stat.attendance_num >= 75 ? 'text-success' : stat.attendance_num >= 60 ? 'text-warning' : 'text-danger'}`}>{stat.attendance}</span>
                    </div>
                  </td>
                </tr>
              ))}
              {filteredStats.length === 0 && (
                <tr>
                  <td colSpan="5" style={{ textAlign: 'center', padding: '2rem', color: '#64748B' }}>No attendance data found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        <div className="table-footer flex-between">
          <span>Showing {filteredStats.length} of {stats.class_wise_stats.length} records</span>
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
