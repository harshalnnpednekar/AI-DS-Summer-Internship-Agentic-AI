import React, { useState } from 'react';
import { Calendar as CalendarIcon, UploadCloud, CheckCircle, Mail, MessageSquare, AlertCircle, Send } from 'lucide-react';
import './Pages.css';
import './AcademicCalendar.css';

const AcademicCalendar = () => {
  const [activeTab, setActiveTab] = useState('All Events');

  const events = [
    { id: 1, title: 'Insem Examinations — Sem V', date: 'Jul 12, 2025', type: 'EXAMINATION', priority: 'High', days: '3d', color: 'danger' },
    { id: 2, title: 'Project Synopsis Submission — TE', date: 'Jul 15, 2025', type: 'SUBMISSION', priority: 'High', days: '6d', color: 'danger' },
    { id: 3, title: 'Faculty Review Meeting — AICTE Compliance', date: 'Jul 18, 2025', type: 'MEETING', priority: 'Medium', days: '9d', color: 'warning' },
    { id: 4, title: 'Guest Lecture: NLP in Industry', date: 'Jul 22, 2025', type: 'EVENT', priority: 'Advisory', days: '13d', color: 'info' }
  ];

  return (
    <div className="page-container">
      <div className="page-header">

        <h1 className="page-title">Academic Calendar & Automated Updates</h1>
        <p className="page-subtitle">Upload the department PDF calendar. The agent parses it and broadcasts deadline alerts automatically.</p>
      </div>

      <div className="upload-zone success">
        <div className="upload-content">
          <CheckCircle size={32} className="text-success mb-2" />
          <h3 className="font-semibold" style={{ fontSize: '1rem' }}>Academic_Calendar_24-25.pdf</h3>
          <p className="text-secondary" style={{ fontSize: '0.875rem' }}>7 events extracted · Click to replace</p>
          <span className="badge badge-success mt-2">PDF Parsed Successfully</span>
        </div>
      </div>

      <div className="calendar-layout-grid">
        {/* Left Column */}
        <div className="events-column">
          <div className="calendar-tabs">
            {['All Events', 'High', 'Medium', 'Advisory'].map(tab => (
              <button 
                key={tab} 
                className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
                onClick={() => setActiveTab(tab)}
              >
                {tab}
              </button>
            ))}
            <span className="tab-count-label">7 events shown</span>
          </div>

          <div className="card events-card">
            <div className="card-header border-none" style={{ padding: '1.25rem 1.5rem' }}>
              <CalendarIcon size={18} className="text-secondary" />
              <h2>Upcoming Critical Deadlines</h2>
            </div>
            
            <div className="events-list">
              {events.map(event => (
                <div key={event.id} className="event-item">
                  <div className={`event-dot bg-${event.color}`}></div>
                  <div className="event-details">
                    <h4>{event.title}</h4>
                    <p>{event.date} <span className="dot-separator">·</span> <span className="event-type">{event.type}</span></p>
                  </div>
                  <div className="event-meta">
                    <span className={`priority-badge ${event.color}`}>{event.priority} {event.priority === 'High' ? 'Priority' : ''}</span>
                    <span className="days-left"><ClockIcon /> {event.days}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="channels-column">
          <div className="card channels-card">
            <div className="card-header" style={{ borderBottom: 'none' }}>
              <Send size={18} className="text-secondary" />
              <div>
                <h2>Broadcast Channel Status</h2>
                <p className="text-secondary" style={{ fontSize: '0.75rem', marginTop: '0.25rem' }}>Automated notification channels</p>
              </div>
            </div>

            <div className="channels-list">
              <div className="channel-item">
                <div className="channel-icon bg-success-light text-success">
                  <Mail size={16} />
                </div>
                <div className="channel-info">
                  <h4>Email</h4>
                  <p>10 min ago</p>
                </div>
                <label className="toggle-switch">
                  <input type="checkbox" defaultChecked />
                  <span className="slider round"></span>
                </label>
              </div>

              <div className="channel-item">
                <div className="channel-icon bg-success-light text-success">
                  <MessageSquare size={16} />
                </div>
                <div className="channel-info">
                  <h4>WhatsApp</h4>
                  <p>10 min ago</p>
                </div>
                <label className="toggle-switch">
                  <input type="checkbox" defaultChecked />
                  <span className="slider round"></span>
                </label>
              </div>

              <div className="channel-item">
                <div className="channel-icon" style={{ backgroundColor: '#F1F5F9', color: '#94A3B8' }}>
                  <AlertCircle size={16} />
                </div>
                <div className="channel-info">
                  <h4>MS Teams</h4>
                  <p>Disabled</p>
                </div>
                <label className="toggle-switch">
                  <input type="checkbox" />
                  <span className="slider round"></span>
                </label>
              </div>
            </div>

            <div className="card-footer">
              <button className="btn btn-primary" style={{ width: '100%', display: 'flex', gap: '0.5rem', justifyContent: 'center' }}>
                <Send size={16} /> Broadcast Now
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const ClockIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-1">
    <circle cx="12" cy="12" r="10"></circle>
    <polyline points="12 6 12 12 16 14"></polyline>
  </svg>
);

export default AcademicCalendar;
