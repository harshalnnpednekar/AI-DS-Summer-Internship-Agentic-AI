import React, { useState } from 'react';
import { Mail, MessageSquare, AlertCircle, CheckCircle2, XCircle } from 'lucide-react';
import './Pages.css';

const BroadcastLogs = () => {
  const [activeFilter, setActiveFilter] = useState('All');
  
  // Using static exact data from the mockup
  const logs = [
    { id: 1, date: 'Jul 9, 2025', time: '09:00 AM', channel: 'Email', type: 'Deadline Reminder', message: 'Insem Exam reminder sent to all SE & TE students', recipients: 412, status: 'Delivered' },

    { id: 3, date: 'Jul 8, 2025', time: '08:30 AM', channel: 'Email', type: 'Defaulter Alert', message: 'Defaulter list notification sent to parents/guardians', recipients: 8, status: 'Delivered' },
    { id: 4, date: 'Jul 7, 2025', time: '05:00 PM', channel: 'MS Teams', type: 'Faculty Notice', message: 'Faculty review meeting agenda distributed', recipients: 14, status: 'Failed' },
    { id: 5, date: 'Jul 7, 2025', time: '10:15 AM', channel: 'Email', type: 'Event Announcement', message: 'Guest lecture on NLP announcement sent', recipients: 480, status: 'Delivered' }
  ];

  const getChannelIcon = (channel) => {
    switch (channel) {
      case 'Email': return <Mail size={14} className="mr-2" />;

      case 'MS Teams': return <AlertCircle size={14} className="mr-2" />; // Using alert as placeholder for teams icon
      default: return null;
    }
  };

  return (
    <div className="page-container">
      <div className="page-header">

        <h1 className="page-title">Broadcast Activity Logs</h1>
        <p className="page-subtitle">Complete audit trail of all automated notifications dispatched by the agent.</p>
      </div>

      <div className="card log-card">
        <div className="log-header">
          <div className="log-title">
            <RadioIcon /> 
            <span>All Broadcasts</span>
            <span className="count-badge">5</span>
          </div>
          <div className="log-filters">
            {['All', 'Email', 'MS Teams'].map(filter => (
              <button 
                key={filter}
                className={`filter-btn ${activeFilter === filter ? 'active' : ''}`}
                onClick={() => setActiveFilter(filter)}
              >
                {filter}
              </button>
            ))}
          </div>
        </div>

        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>TIMESTAMP</th>
                <th>CHANNEL</th>
                <th>TYPE</th>
                <th>MESSAGE</th>
                <th>RECIPIENTS</th>
                <th>STATUS</th>
              </tr>
            </thead>
            <tbody>
              {logs.map(log => (
                <tr key={log.id}>
                  <td>
                    <div className="td-date">{log.date}</div>
                    <div className="td-time">{log.time}</div>
                  </td>
                  <td>
                    <div className="channel-badge">
                      {getChannelIcon(log.channel)}
                      {log.channel}
                    </div>
                  </td>
                  <td>{log.type}</td>
                  <td className="message-cell">{log.message}</td>
                  <td>{log.recipients}</td>
                  <td>
                    <div className={`status-badge ${log.status.toLowerCase()}`}>
                      {log.status === 'Delivered' ? <CheckCircle2 size={14} /> : <XCircle size={14} />}
                      <span>{log.status}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        <div className="table-footer">
          Showing 5 of 5 records
        </div>
      </div>
    </div>
  );
};

const RadioIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="2"></circle>
    <path d="M16.24 7.76a6 6 0 0 1 0 8.49m-8.48-.01a6 6 0 0 1 0-8.49m11.31-2.82a10 10 0 0 1 0 14.14m-14.14 0a10 10 0 0 1 0-14.14"></path>
  </svg>
);

export default BroadcastLogs;
