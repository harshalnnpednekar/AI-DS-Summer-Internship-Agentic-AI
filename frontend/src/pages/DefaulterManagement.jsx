import React from 'react';
import { AlertTriangle, Download, Send, CheckSquare, Square } from 'lucide-react';
import './Pages.css';
import './DefaulterManagement.css';

const DefaulterManagement = () => {
  const students = [
    { id: 'VESIT/23/DS/0041', name: 'Aarav Khanna', class: 'SE-B', attendance: 68, status: 'At Risk', checked: false },
    { id: 'VESIT/23/DS/0078', name: 'Priyanka Joshi', class: 'SE-B', attendance: 71, status: 'At Risk', checked: false },
    { id: 'VESIT/22/DS/0115', name: 'Rohan Patil', class: 'TE-B', attendance: 62, status: 'At Risk', checked: false },
    { id: 'VESIT/22/DS/0132', name: 'Sneha Raut', class: 'TE-B', attendance: 59, status: 'Critical', checked: false },
    { id: 'VESIT/22/DS/0089', name: 'Mihir Tiwari', class: 'TE-B', attendance: 64, status: 'At Risk', checked: false },
    { id: 'VESIT/22/DS/0201', name: 'Divya Kulkarni', class: 'TE-B', attendance: 55, status: 'Critical', checked: false },
    { id: 'VESIT/22/DS/0167', name: 'Yash Shinde', class: 'TE-B', attendance: 48, status: 'Critical', checked: true },
    { id: 'VESIT/21/DS/0055', name: 'Aniket Sharma', class: 'BE-A', attendance: 73, status: 'At Risk', checked: false }
  ];

  return (
    <div className="page-container">
      <div className="page-header">

        <h1 className="page-title">Automated Defaulter Management</h1>
        <p className="page-subtitle">Auto-generated from live attendance data. Awaiting HOD approval before broadcast.</p>
      </div>

      <div className="card" style={{ padding: 0 }}>
        <div className="defaulter-action-bar">
          <div className="defaulter-info">
            <AlertTriangle className="text-danger" size={20} />
            <span className="font-semibold" style={{ color: 'var(--color-text-primary)' }}>Defaulter List — Auto-Generated</span>
            <div className="vertical-divider"></div>
            <span className="text-secondary" style={{ fontSize: '0.875rem' }}>
              Criteria: <span style={{ color: 'var(--color-danger)', fontWeight: 500 }}>Attendance &lt; 75%</span>
            </span>
            <div className="vertical-divider"></div>
            <span className="font-semibold text-sm">8 students identified</span>
            <span className="text-secondary text-sm ml-1">· Generated Jul 9, 2025</span>
          </div>
          <div className="defaulter-actions">
            <button className="btn btn-outline" style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <Download size={16} /> Export Official PDF
            </button>
            <button className="btn btn-primary" style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <Send size={16} /> Approve & Broadcast Defaulter List <span className="action-badge">1</span>
            </button>
          </div>
        </div>

        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ width: '40px' }}><Square size={18} color="var(--color-border-focus)" /></th>
                <th>STUDENT ID</th>
                <th>STUDENT NAME</th>
                <th>CLASS</th>
                <th>ATTENDANCE %</th>
                <th>STATUS</th>
              </tr>
            </thead>
            <tbody>
              {students.map((s, index) => (
                <tr key={index} className={s.checked ? 'selected-row' : ''}>
                  <td>
                    {s.checked ? (
                      <CheckSquare size={18} color="var(--color-primary)" />
                    ) : (
                      <Square size={18} color="var(--color-border-focus)" />
                    )}
                  </td>
                  <td className="font-medium">{s.id}</td>
                  <td>{s.name}</td>
                  <td>
                    <span className="class-badge">{s.class}</span>
                  </td>
                  <td>
                    <div className="progress-cell">
                      <div className="progress-bar-bg">
                        <div 
                          className={`progress-bar-fill ${s.attendance < 60 ? 'bg-danger' : 'bg-warning'}`} 
                          style={{ width: `${s.attendance}%` }}
                        ></div>
                      </div>
                      <span className="font-semibold" style={{ fontSize: '0.875rem' }}>{s.attendance}%</span>
                    </div>
                  </td>
                  <td>
                    <span className={`status-badge-outline ${s.status === 'Critical' ? 'critical' : 'risk'}`}>
                      {s.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="table-footer" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span className="font-medium text-sm">1 of 8 selected</span>
          <span className="text-success text-sm flex-center" style={{ gap: '0.25rem' }}>
            <CheckCircle2Icon /> Pending HOD approval before broadcast
          </span>
        </div>
      </div>
    </div>
  );
};

const CheckCircle2Icon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
    <polyline points="22 4 12 14.01 9 11.01"></polyline>
  </svg>
);

export default DefaulterManagement;
