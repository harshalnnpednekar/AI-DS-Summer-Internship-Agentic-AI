import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, BookOpen, Edit, Users, Calendar, CheckCircle2, Search } from 'lucide-react';
import './Pages.css';
import './Dashboard.css';

const getAcademicYear = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth();
  // Assume academic year starts in June (month 5)
  if (month >= 5) {
    return `${year}-${(year + 1).toString().slice(2)}`;
  } else {
    return `${year - 1}-${year.toString().slice(2)}`;
  }
};

const Dashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({ total_lectures: 0, avg_attendance: 0, recent_lectures: [], class_wise_stats: [] });
  const [filter, setFilter] = useState('All');
  const [search, setSearch] = useState('');
  const filteredStats = (stats.class_wise_stats || []).filter(stat => {
    const matchesFilter = filter === 'All' || stat.class.startsWith(filter);
    const matchesSearch = stat.class.toLowerCase().includes(search.toLowerCase()) || 
                          stat.subject.toLowerCase().includes(search.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    const role = localStorage.getItem('userRole');

    // Guard: students should never see the faculty dashboard
    if (role === 'STUDENT') {
      navigate('/student-dashboard', { replace: true });
      return;
    }

    const fetchStats = async () => {
      try {
        // Ensure HOD has a faculty_profile row (one-time repair for accounts created before the fix)
        if (role === 'HOD') {
          await fetch('/api/auth/repair-profile', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
          }).catch(() => {});
        }

        const response = await fetch(`/api/attendance/stats?t=${Date.now()}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        const data = await response.json();
        if (data.success) {
          setStats(data.data);
        }
      } catch (err) {
        console.error("Failed to fetch stats", err);
      }
    };
    fetchStats();
  }, []);

  const [userInfo, setUserInfo] = useState({
    name: localStorage.getItem('userName') || 'User',
    desc: localStorage.getItem('userDesc') || 'Faculty',
    role: localStorage.getItem('userRole') || 'HOD'
  });

  useEffect(() => {
    const handleProfileUpdate = () => {
      setUserInfo({
        name: localStorage.getItem('userName') || 'User',
        desc: localStorage.getItem('userDesc') || 'Faculty',
        role: localStorage.getItem('userRole') || 'HOD'
      });
    };
    window.addEventListener('profileUpdated', handleProfileUpdate);
    return () => window.removeEventListener('profileUpdated', handleProfileUpdate);
  }, []);

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Good morning, {userInfo.name} 👋</h1>
        <p className="page-subtitle">Academic Year {getAcademicYear()} · {userInfo.desc}</p>
      </div>

      <div className="stats-grid">
        <div className="card stat-card">
          <div className="stat-header">
            <h3>{userInfo.role === 'HOD' ? "CLASSES' AVG. ATTENDANCE" : "MY CLASSES' AVG. ATTENDANCE"}</h3>
            <div className="stat-icon bg-success-light text-success">
              <TrendingUp size={18} />
            </div>
          </div>
          <div className="stat-value">{stats.avg_attendance}%</div>
          <div className="stat-context">Current Semester</div>
        </div>

        <div className="card stat-card">
          <div className="stat-header">
            <h3>TOTAL LECTURES CONDUCTED</h3>
            <div className="stat-icon bg-secondary-light text-secondary">
              <BookOpen size={18} />
            </div>
          </div>
          <div className="stat-value">{stats.total_lectures}</div>
          <div className="stat-context">Current Semester</div>
        </div>
      </div>

      <div className="quick-actions-grid">
        <div className="card action-card">
          <div className="action-icon text-primary">
            <Edit size={24} />
          </div>
          <h3>Mark Attendance</h3>
          <p>Submit today's lecture attendance record</p>
          <button className="btn-text action-link" onClick={() => navigate('/mark-attendance')}>Open &gt;</button>
        </div>

        <div className="card action-card">
          <div className="action-icon text-secondary">
            <Users size={24} />
          </div>
          <h3>Attendance Data</h3>
          <p>{userInfo.role === 'HOD' ? 'View attendance stats for department classes' : 'View attendance stats for your classes'}</p>
          <button className="btn-text action-link" onClick={() => navigate('/attendance-data')}>Open &gt;</button>
        </div>

        <div className="card action-card">
          <div className="action-icon" style={{ color: '#8B5CF6' }}>
            <Calendar size={24} />
          </div>
          <h3>Academic Calendar</h3>
          <p>View upcoming deadlines and events</p>
          <button className="btn-text action-link" onClick={() => navigate('/calendar')}>Open &gt;</button>
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

export default Dashboard;


const UsersIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-secondary mr-2">
    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path>
    <circle cx="9" cy="7" r="4"></circle>
    <path d="M22 21v-2a4 4 0 0 0-3-3.87"></path>
    <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
  </svg>
);
