import React from 'react';
import { TrendingUp, BookOpen, Edit, Users, Calendar, CheckCircle2 } from 'lucide-react';
import './Pages.css';
import './Dashboard.css';

const Dashboard = () => {
  return (
    <div className="page-container">
      <div className="page-header">
        <div className="breadcrumb">Dashboard &gt; Overview</div>
        <h1 className="page-title">Good morning, Dr. Priya 👋</h1>
        <p className="page-subtitle">Academic Year 2024-25 · Faculty — SE-A Data Structures & Algorithms</p>
      </div>

      <div className="agent-status-banner">
        <div className="status-indicator online"></div>
        <span>Agent Running — All systems operational</span>
      </div>

      <div className="stats-grid">
        <div className="card stat-card">
          <div className="stat-header">
            <h3>MY CLASSES' AVG. ATTENDANCE</h3>
            <div className="stat-icon bg-success-light text-success">
              <TrendingUp size={18} />
            </div>
          </div>
          <div className="stat-value">88%</div>
          <div className="stat-context">SE-A — Data Structures & Algorithms</div>
        </div>

        <div className="card stat-card">
          <div className="stat-header">
            <h3>TOTAL LECTURES CONDUCTED</h3>
            <div className="stat-icon bg-secondary-light text-secondary">
              <BookOpen size={18} />
            </div>
          </div>
          <div className="stat-value">42</div>
          <div className="stat-context">Current semester</div>
        </div>
      </div>

      <div className="quick-actions-grid">
        <div className="card action-card">
          <div className="action-icon text-primary">
            <Edit size={24} />
          </div>
          <h3>Mark Attendance</h3>
          <p>Submit today's lecture attendance record</p>
          <button className="btn-text action-link">Open &gt;</button>
        </div>

        <div className="card action-card">
          <div className="action-icon text-secondary">
            <Users size={24} />
          </div>
          <h3>My Attendance Data</h3>
          <p>View attendance stats for your classes</p>
          <button className="btn-text action-link">Open &gt;</button>
        </div>

        <div className="card action-card">
          <div className="action-icon" style={{ color: '#8B5CF6' }}>
            <Calendar size={24} />
          </div>
          <h3>Academic Calendar</h3>
          <p>View upcoming deadlines and events</p>
          <button className="btn-text action-link">Open &gt;</button>
        </div>
      </div>

      <div className="card activity-card">
        <div className="activity-header">
          <TrendingUp size={18} className="text-secondary" />
          <h2>Recent Agent Activity</h2>
        </div>
        
        <div className="activity-list">
          <div className="activity-item">
            <div className="activity-indicator"></div>
            <div className="activity-content">
              <h4>Insem Exam reminder sent to all SE & TE students</h4>
              <p>Jul 9, 2025 · 09:00 AM · via Email</p>
            </div>
            <div className="status-badge delivered">Delivered</div>
          </div>
          
          <div className="activity-item">
            <div className="activity-indicator"></div>
            <div className="activity-content">
              <h4>Insem Exam reminder broadcast to department group</h4>
              <p>Jul 9, 2025 · 09:01 AM · via WhatsApp</p>
            </div>
            <div className="status-badge delivered">Delivered</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
