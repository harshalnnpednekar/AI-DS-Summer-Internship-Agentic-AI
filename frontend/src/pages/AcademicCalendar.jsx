import React, { useState, useEffect } from 'react';
import { Calendar as CalendarIcon, UploadCloud, CheckCircle, Mail, MessageSquare, AlertCircle, Send } from 'lucide-react';
import './Pages.css';
import './AcademicCalendar.css';

const classifyEvent = (title) => {
  const titleLower = title.toLowerCase();
  if (titleLower.includes('exam') || titleLower.includes('submission') || titleLower.includes('test') || titleLower.includes('defaulter') || titleLower.includes('kt')) {
    return { priority: 'High', color: 'danger' };
  } else if (titleLower.includes('meeting') || titleLower.includes('term') || titleLower.includes('review') || titleLower.includes('result')) {
    return { priority: 'Medium', color: 'warning' };
  }
  return { priority: 'Advisory', color: 'info' };
};

const calculateDays = (dateString) => {
  const eventDate = new Date(dateString);
  const today = new Date();
  
  // Reset time part to compare just dates
  today.setHours(0, 0, 0, 0);
  eventDate.setHours(0, 0, 0, 0);

  const diffTime = eventDate - today;
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays < 0) return 'Past';
  if (diffDays === 0) return 'Today';
  return `${diffDays}d`;
};

const AcademicCalendar = () => {
  const userRole = localStorage.getItem('userRole');
  const showBroadcast = userRole === 'HOD' || userRole === 'FACULTY';
  
  const [activeTab, setActiveTab] = useState('All Events');
  const [events, setEvents] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null); // 'success', 'error', null
  const [fileName, setFileName] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const token = localStorage.getItem('accessToken');
        const response = await fetch('/api/events/events', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        if (data.success) {
          const mappedEvents = data.data.events.map((ev, index) => {
            const classification = classifyEvent(ev.title);
            return {
              id: ev.id || `event-${index}`,
              title: ev.title,
              date: ev.date,
              type: ev.department === 'ALL' ? 'GENERAL' : 'DEPARTMENTAL',
              priority: classification.priority,
              days: calculateDays(ev.date),
              color: classification.color
            };
          });
          setEvents(mappedEvents);
        }
      } catch (err) {
        console.error("Failed to fetch calendar events", err);
      }
    };
    fetchEvents();
  }, []);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      setUploadStatus('error');
      setErrorMessage('Only PDF files are allowed');
      return;
    }

    setFileName(file.name);
    setIsUploading(true);
    setUploadStatus(null);
    setErrorMessage('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch('/api/events/extract', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,
      });

      // Handle auth errors — session expired
      if (response.status === 401 || response.status === 403) {
        setUploadStatus('error');
        setErrorMessage('Session expired. Please log out and log in again.');
        setIsUploading(false);
        return;
      }

      const data = await response.json();
      
      if (data.success) {
        setUploadStatus('success');
        
        // After successful upload, fetch all events again to refresh the list
        const response2 = await fetch('/api/events/events', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data2 = await response2.json();
        if (data2.success) {
          const mappedEvents = data2.data.events.map((ev, index) => {
            const classification = classifyEvent(ev.title);
            return {
              id: ev.id || `event-${index}`,
              title: ev.title,
              date: ev.date,
              type: ev.department === 'ALL' ? 'GENERAL' : 'DEPARTMENTAL',
              priority: classification.priority,
              days: calculateDays(ev.date),
              color: classification.color
            };
          });
          setEvents(mappedEvents);
        }
      } else {
        setUploadStatus('error');
        setErrorMessage(data.error || data.detail || 'Failed to extract events');
      }
    } catch (err) {
      setUploadStatus('error');
      setErrorMessage('Network error occurred during upload');
    } finally {
      setIsUploading(false);
    }
  };

  const filteredEvents = activeTab === 'All Events' 
    ? events 
    : events.filter(event => event.priority === activeTab);

  return (
    <div className="page-container">
      <div className="page-header">

        <h1 className="page-title">{showBroadcast ? 'Academic Calendar & Automated Updates' : 'Upcoming Events'}</h1>
        <p className="page-subtitle">{showBroadcast ? 'Upload the department PDF calendar. The agent parses it and broadcasts deadline alerts automatically.' : 'Upcoming deadlines and department events.'}</p>
      </div>

      {showBroadcast && (
        <div className={`upload-zone ${uploadStatus === 'success' ? 'success' : uploadStatus === 'error' ? 'error' : ''}`} style={{ cursor: 'pointer' }} onClick={() => document.getElementById('fileUpload').click()}>
          <input 
            type="file" 
            id="fileUpload" 
            accept=".pdf" 
            style={{ display: 'none' }} 
            onChange={handleFileUpload} 
          />
          <div className="upload-content">
            {isUploading ? (
              <>
                <UploadCloud size={32} className="text-secondary mb-2" />
                <h3 className="font-semibold" style={{ fontSize: '1rem' }}>Parsing PDF...</h3>
                <p className="text-secondary" style={{ fontSize: '0.875rem' }}>Please wait while the AI extracts events.</p>
              </>
            ) : uploadStatus === 'success' ? (
              <>
                <CheckCircle size={32} className="text-success mb-2" />
                <h3 className="font-semibold" style={{ fontSize: '1rem' }}>{fileName}</h3>
                <p className="text-secondary" style={{ fontSize: '0.875rem' }}>{events.length} events extracted · Click to replace</p>
                <span className="badge badge-success mt-2">PDF Parsed Successfully</span>
              </>
            ) : uploadStatus === 'error' ? (
              <>
                <AlertCircle size={32} className="text-danger mb-2" />
                <h3 className="font-semibold" style={{ fontSize: '1rem' }}>Upload Failed</h3>
                <p className="text-secondary" style={{ fontSize: '0.875rem' }}>{errorMessage} · Click to retry</p>
                <span className="badge badge-danger mt-2">Error Parsing PDF</span>
              </>
            ) : (
              <>
                <UploadCloud size={32} className="text-primary mb-2" />
                <h3 className="font-semibold" style={{ fontSize: '1rem' }}>Upload Academic Calendar</h3>
                <p className="text-secondary" style={{ fontSize: '0.875rem' }}>Drag & drop your PDF here or click to browse</p>
              </>
            )}
          </div>
        </div>
      )}

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
            <span className="tab-count-label">{filteredEvents.length} events shown</span>
          </div>

          <div className="card events-card">
            <div className="card-header border-none" style={{ padding: '1.25rem 1.5rem' }}>
              <CalendarIcon size={18} className="text-secondary" />
              <h2>Upcoming Critical Deadlines</h2>
            </div>
            
            <div className="events-list">
              {filteredEvents.map(event => (
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
        {showBroadcast && (
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
                </div>
                <label className="toggle-switch">
                  <input type="checkbox" defaultChecked />
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
        )}
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
