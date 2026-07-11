import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, BookOpen, Edit, Users, Calendar, CheckCircle2 } from 'lucide-react';
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
  const [stats, setStats] = useState({ total_lectures: 0, avg_attendance: 0, recent_lectures: [] });
  const [selectedLecture, setSelectedLecture] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    const role = localStorage.getItem('userRole');

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

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Good morning, {localStorage.getItem('userName') || 'User'} 👋</h1>
        <p className="page-subtitle">Academic Year {getAcademicYear()} · {localStorage.getItem('userDesc') || 'Faculty'}</p>
      </div>

      <div className="stats-grid">
        <div className="card stat-card">
          <div className="stat-header">
            <h3>{localStorage.getItem('userRole') === 'HOD' ? "CLASSES' AVG. ATTENDANCE" : "MY CLASSES' AVG. ATTENDANCE"}</h3>
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
          <h3>{localStorage.getItem('userRole') === 'HOD' ? 'Attendance Data' : 'My Attendance Data'}</h3>
          <p>{localStorage.getItem('userRole') === 'HOD' ? 'View attendance stats for department classes' : 'View attendance stats for your classes'}</p>
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

      <div className="card activity-card">
        <div className="activity-header">
          <BookOpen size={18} className="text-secondary" />
          <h2>Recent Attendance Submissions</h2>
        </div>
        
        <div className="activity-list">
          {stats.recent_lectures && stats.recent_lectures.length > 0 ? (
            stats.recent_lectures.map(lecture => (
              <div className="activity-item" key={lecture.id} style={{ flexDirection: 'column', alignItems: 'stretch' }}>
                <div style={{ display: 'flex', width: '100%', gap: '1rem', alignItems: 'flex-start' }}>
                  <div className="activity-indicator" style={{ backgroundColor: '#10B981' }}></div>
                <div className="activity-content" style={{ flex: 1 }}>
                  <h4>{lecture.class_name} • {lecture.subject_name} <span style={{fontWeight: 'normal', color: 'var(--color-text-secondary)', fontSize: '0.9em'}}>({lecture.session_type === 'Lecture' ? 'Theory' : lecture.session_type === 'Lab' ? 'Practical' : lecture.session_type || 'Theory'})</span></h4>
                  <p>{lecture.date} · Topic: {lecture.topic} · Attendance: {lecture.present}/{lecture.total}</p>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                  <button 
                    style={{ background: 'white', border: '1px solid var(--color-border)', borderRadius: '4px', padding: '4px 12px', fontSize: '12px', cursor: 'pointer', fontWeight: 500 }}
                    onClick={() => setSelectedLecture(selectedLecture?.id === lecture.id ? null : lecture)}
                  >
                    {selectedLecture?.id === lecture.id ? 'Hide Roll List' : 'View Roll List'}
                  </button>
                  <div className="status-badge delivered">Submitted</div>
                </div>
                </div>

                {selectedLecture?.id === lecture.id && (
                  <div style={{ marginTop: '1rem', padding: '1.5rem', backgroundColor: '#F8FAFC', borderRadius: '8px', border: '1px solid var(--color-border)', marginLeft: '1.5rem' }}>
                    <div style={{ marginBottom: '1.5rem' }}>
                      <h3 style={{ fontSize: '0.875rem', color: '#10B981', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Present ({lecture.present})</h3>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                        {Array.from({length: lecture.total}, (_, i) => String(i + 1))
                          .filter(r => !(lecture.absentees || []).includes(r))
                          .map(r => <span key={r} style={{ background: '#dcfce7', color: '#166534', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.8125rem', fontWeight: 600 }}>{r}</span>)}
                      </div>
                    </div>
                    <div>
                      <h3 style={{ fontSize: '0.875rem', color: '#EF4444', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Absent ({lecture.total - lecture.present})</h3>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                        {lecture.absentees && lecture.absentees.length > 0 ? lecture.absentees.map(r => (
                          <span key={r} style={{ background: '#fee2e2', color: '#991b1b', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.8125rem', fontWeight: 600 }}>{r}</span>
                        )) : <span style={{ color: 'var(--color-text-secondary)', fontSize: '0.8125rem' }}>None</span>}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="activity-item">
              <p style={{ color: '#64748B', padding: '1rem 0' }}>No attendance records submitted yet.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
