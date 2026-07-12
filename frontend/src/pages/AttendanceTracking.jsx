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
  const [selectedLecture, setSelectedLecture] = useState(null);
  const [showAllRecent, setShowAllRecent] = useState(false);
  
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

  
  const recentLectures = showAllRecent ? (stats.recent_lectures || []) : (stats.recent_lectures || []).slice(0, 5);

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

      <div className="card activity-card">
        <div className="activity-header">
          <BookOpen size={18} className="text-secondary" />
          <h2>Recent Attendance Submissions</h2>
        </div>
        
        <div className="activity-list">
          {recentLectures && recentLectures.length > 0 ? (
            recentLectures.map(lecture => (
              <div className="activity-item" key={lecture.id} style={{ flexDirection: 'column', alignItems: 'stretch' }}>
                <div style={{ display: 'flex', width: '100%', gap: '1rem', alignItems: 'flex-start' }}>
                  <div className="activity-indicator" style={{ backgroundColor: '#10B981' }}></div>
                <div className="activity-content" style={{ flex: 1 }}>
                  <h4>{lecture.class_name} • {lecture.subject_name} <span style={{fontWeight: 'normal', color: 'var(--color-text-secondary)', fontSize: '0.9em'}}>({lecture.session_type === 'Lecture' ? 'Theory' : lecture.session_type === 'Lab' ? 'Practical' : lecture.session_type || 'Theory'})</span></h4>
                  <p>{lecture.date} · {lecture.time_slot ? lecture.time_slot + ' · ' : ''}Topic: {lecture.topic} · Attendance: {lecture.present}/{lecture.total}</p>
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
        
        {stats.recent_lectures && stats.recent_lectures.length > 5 && (
          <div style={{ textAlign: 'center', marginTop: '1rem', padding: '1rem 0', borderTop: '1px solid var(--color-border)' }}>
            <button 
              onClick={() => setShowAllRecent(!showAllRecent)}
              style={{ background: 'none', border: 'none', color: '#3B82F6', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', margin: '0 auto' }}
            >
              {showAllRecent ? 'Show Less' : 'View All Records (+)'}
            </button>
          </div>
        )}
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
