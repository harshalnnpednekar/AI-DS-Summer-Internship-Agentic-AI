import React, { useState, useEffect } from 'react';
import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Calendar, 
  Users, 
  AlertTriangle, 
  FileText, 
  Radio, 
  Settings, 
  LogOut,
  Edit,
  Cpu,
  Award
} from 'lucide-react';
import './Layout.css';

const Layout = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const timeString = currentTime.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  }).toLowerCase();

  const dateString = currentTime.toLocaleDateString('en-US', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  });

  const [userInfo, setUserInfo] = useState({
    role: localStorage.getItem('userRole') || 'HOD',
    name: localStorage.getItem('userName') || 'Dr. M. Vijayalakshmi',
    desc: localStorage.getItem('userDesc') || 'Head of Department',
    initials: localStorage.getItem('userInitials') || 'MV'
  });

  useEffect(() => {
    const handleProfileUpdate = () => {
      setUserInfo({
        role: localStorage.getItem('userRole') || 'HOD',
        name: localStorage.getItem('userName') || 'Dr. M. Vijayalakshmi',
        desc: localStorage.getItem('userDesc') || 'Head of Department',
        initials: localStorage.getItem('userInitials') || 'MV'
      });
    };
    window.addEventListener('profileUpdated', handleProfileUpdate);
    return () => window.removeEventListener('profileUpdated', handleProfileUpdate);
  }, []);

  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const response = await fetch('/api/events/upcoming?days=7');
        const data = await response.json();
        if (Array.isArray(data)) {
          setNotifications(data);
        }
      } catch (err) {
        console.error("Failed to fetch notifications");
      }
    };
    fetchNotifications();
    
    // Poll every 30 seconds for live updates
    const pollTimer = setInterval(fetchNotifications, 30000);
    return () => clearInterval(pollTimer);
  }, []);

  return (
    <div className="layout-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-logo">
            <img src="/VESIT LOGO.jpg" alt="VESIT Logo" className="brand-icon-image" />
          </div>
          <div className="brand-text">
            <h2>VESIT</h2>
            <p>AI & DS</p>
          </div>
        </div>

        <nav className="sidebar-nav">
          {userInfo.role !== 'STUDENT' && (
            <div className="nav-section">
              <h3 className="nav-section-title">FACULTY PORTAL</h3>
              <NavLink to="/mark-attendance" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
                <Edit size={20} />
                <span>Mark Attendance</span>
              </NavLink>
            </div>
          )}

          <div className="nav-section mt-4">
            <h3 className="nav-section-title">{userInfo.role === 'STUDENT' ? 'STUDENT PORTAL' : 'MANAGEMENT'}</h3>
            <NavLink to="/dashboard" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
              <LayoutDashboard size={20} />
              <span>Overview</span>
            </NavLink>
            <NavLink to="/calendar" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
              <Calendar size={20} />
              <span>{userInfo.role === 'STUDENT' ? 'Upcoming Events' : 'Academic Calendar'}</span>
            </NavLink>
            <NavLink to="/attendance-data" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
              <Users size={20} />
              <span>{userInfo.role === 'STUDENT' ? 'My Attendance' : 'Attendance Tracking'}</span>
            </NavLink>
            {userInfo.role === 'STUDENT' && (
              <NavLink to="/certificates" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
                <Award size={20} />
                <span>My Certificates</span>
              </NavLink>
            )}
            {(userInfo.role === 'HOD' || userInfo.role === 'FACULTY') && (
              <NavLink to="/defaulter-management" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
                <AlertTriangle size={20} />
                <span>Defaulter Management</span>
              </NavLink>
            )}
            {userInfo.role === 'HOD' && (
              <>
                <NavLink to="/reports" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
                  <FileText size={20} />
                  <span>Reports & Exports</span>
                </NavLink>
                <NavLink to="/broadcast-logs" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
                  <Radio size={20} />
                  <span>Broadcast Logs</span>
                </NavLink>
                <NavLink to="/configuration" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
                  <Settings size={20} />
                  <span>Configuration</span>
                </NavLink>
              </>
            )}
          </div>
        </nav>

        <div className="sidebar-footer">
          <div 
            className="user-profile" 
            onClick={() => navigate('/profile')}
            style={{ cursor: 'pointer' }}
            title="View your profile"
          >
            <div className="user-avatar mv-avatar">{userInfo.initials}</div>
            <div className="user-info">
               <h4>{userInfo.name}</h4>
              <p>{userInfo.desc}</p>
            </div>
          </div>
          <button className="logout-btn" onClick={() => {
            localStorage.clear();
            navigate('/login');
          }}>
            <LogOut size={18} />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="main-content">
        {/* Header */}
        <header className="top-header">
          <div className="header-left">
            <div className="agent-status">
              <Cpu size={18} />
              <span>OmniSync</span>
            </div>
          </div>
          <div className="header-right">
            <div className="datetime">
              <strong>{timeString}</strong>
              <p>{dateString}</p>
            </div>
            <div style={{ position: 'relative' }}>
              <button 
                className="notification-btn hover-scale"
                onClick={() => setShowNotifications(!showNotifications)}
              >
                <span className="notification-icon">🔔</span>
                {notifications.length > 0 && (
                  <span className="notification-badge pulse-anim">{notifications.length}</span>
                )}
              </button>
              
              {showNotifications && (
                <div style={{
                  position: 'absolute', top: '120%', right: '0', 
                  background: 'white', border: '1px solid #e2e8f0', 
                  borderRadius: '12px', padding: '16px', minWidth: '300px',
                  boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)', 
                  zIndex: 100, textAlign: 'left'
                }}>
                  <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', borderBottom: '1px solid #e2e8f0', paddingBottom: '8px', color: '#1e293b' }}>
                    Live Notifications
                  </h4>
                  {notifications.length === 0 ? (
                    <p style={{ fontSize: '13px', color: '#64748b', margin: 0 }}>You're all caught up!</p>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '300px', overflowY: 'auto' }}>
                      {notifications.map((notif, idx) => (
                        <div key={idx} style={{ paddingBottom: idx < notifications.length - 1 ? '12px' : '0', borderBottom: idx < notifications.length - 1 ? '1px solid #f1f5f9' : 'none' }}>
                          <strong style={{ fontSize: '13px', display: 'block', color: '#0f172a', marginBottom: '4px' }}>{notif.title}</strong>
                          <span style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '2px' }}>{notif.description || 'No details provided'}</span>
                          <span style={{ fontSize: '11px', color: '#4f46e5', fontWeight: '500' }}>
                            {new Date(notif.date).toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' })}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="page-content slide-up-anim">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
