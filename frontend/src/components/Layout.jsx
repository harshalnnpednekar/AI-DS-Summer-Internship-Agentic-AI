import React from 'react';
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
  Cpu
} from 'lucide-react';
import './Layout.css';

const Layout = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // Redirect to login if unauthenticated (mock behavior for layout)
  // In a real app this would check a token

  return (
    <div className="layout-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-logo">
            <Cpu size={24} color="var(--color-secondary)" />
          </div>
          <div className="brand-text">
            <h2>VESIT</h2>
            <p>AI & Data Science Dept.</p>
          </div>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-section">
            <h3 className="nav-section-title">FACULTY PORTAL</h3>
            <NavLink to="/mark-attendance" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
              <Edit size={20} />
              <span>Mark Attendance</span>
            </NavLink>
          </div>

          <div className="nav-section mt-4">
            <h3 className="nav-section-title">MANAGEMENT</h3>
            <NavLink to="/dashboard" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
              <LayoutDashboard size={20} />
              <span>Overview</span>
            </NavLink>
            <NavLink to="/calendar" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
              <Calendar size={20} />
              <span>Academic Calendar</span>
            </NavLink>
            <NavLink to="/attendance-data" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
              <Users size={20} />
              <span>Attendance Tracking</span>
            </NavLink>
            <NavLink to="/defaulter-management" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
              <AlertTriangle size={20} />
              <span>Defaulter Management</span>
              <span className="nav-badge">8</span>
            </NavLink>
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
          </div>
        </nav>

        <div className="sidebar-footer">
          <div className="user-profile">
            <div className="user-avatar hk-avatar">HK</div>
            <div className="user-info">
              <h4>Dr. H. Khandelwal</h4>
              <p>Head of Department</p>
            </div>
          </div>
          <button className="logout-btn" onClick={() => navigate('/login')}>
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
              <span>Department Management Agent</span>
              <span className="badge badge-success" style={{ marginLeft: '8px', fontSize: '10px' }}>LIVE</span>
            </div>
          </div>
          <div className="header-right">
            <div className="datetime">
              <strong>04:52 pm</strong>
              <p>Thu, 9 Jul, 2026</p>
            </div>
            <button className="notification-btn hover-scale">
              <span className="notification-icon">🔔</span>
              <span className="notification-badge pulse-anim">2</span>
            </button>
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
