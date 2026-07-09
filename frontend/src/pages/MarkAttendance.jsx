import React, { useState } from 'react';
import { Edit2, Calendar, Send, Info } from 'lucide-react';
import './Pages.css';
import './MarkAttendance.css';

const MarkAttendance = () => {
  const [topic, setTopic] = useState('');
  const [totalStudents, setTotalStudents] = useState('');
  const [studentsPresent, setStudentsPresent] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // form submission logic would go here
    setTopic('');
    setTotalStudents('');
    setStudentsPresent('');
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div className="breadcrumb">Dashboard &gt; Mark Attendance</div>
        <h1 className="page-title">Mark Lecture Attendance</h1>
        <p className="page-subtitle">Submit attendance details for your lecture. Data is reflected immediately in the tracking dashboard.</p>
      </div>

      <div className="attendance-grid">
        {/* Form Column */}
        <div className="card form-card">
          <div className="card-header">
            <Edit2 size={18} className="text-secondary" />
            <h2>Lecture Attendance Entry</h2>
          </div>

          <form onSubmit={handleSubmit} className="attendance-form">
            <div className="form-group">
              <label>Class & Subject <span className="text-danger">*</span></label>
              <select className="form-select" defaultValue="SE-A">
                <option value="SE-A">SE-A — Data Structures & Algorithms</option>
                <option value="TE-A">TE-A — Database Management</option>
              </select>
              <div className="field-hint">
                <span className="badge badge-dark">SE-A</span>
                <span className="hint-text">· 42 lectures held so far · Current avg: <strong className="text-success">88%</strong></span>
              </div>
            </div>

            <div className="form-group">
              <label>Lecture Date <span className="text-danger">*</span></label>
              <div className="input-with-icon">
                <input type="date" defaultValue="2026-07-09" className="form-input" required />
                {/* Modern browsers show their own calendar icon, this is styled appropriately in CSS */}
              </div>
            </div>

            <div className="form-group">
              <label>Lecture Topic / Module <span className="text-danger">*</span></label>
              <input 
                type="text" 
                className="form-input" 
                placeholder="e.g. Binary Trees — Traversal Methods" 
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                required 
              />
            </div>

            <div className="form-row">
              <div className="form-group half">
                <label>Total Students <span className="text-danger">*</span></label>
                <input 
                  type="number" 
                  className="form-input" 
                  placeholder="e.g. 60" 
                  min="1"
                  value={totalStudents}
                  onChange={(e) => setTotalStudents(e.target.value)}
                  required 
                />
              </div>
              <div className="form-group half">
                <label>Students Present <span className="text-danger">*</span></label>
                <input 
                  type="number" 
                  className="form-input" 
                  placeholder="e.g. 52" 
                  min="0"
                  max={totalStudents || 100}
                  value={studentsPresent}
                  onChange={(e) => setStudentsPresent(e.target.value)}
                  required 
                />
              </div>
            </div>

            <button type="submit" className="btn btn-primary submit-btn">
              <Send size={16} /> Submit Attendance Record
            </button>
          </form>
        </div>

        {/* Info Column */}
        <div className="card info-card">
          <div className="card-header border-none">
            <h2>How It Works</h2>
          </div>
          
          <div className="steps-list">
            <div className="step-item">
              <div className="step-number">1</div>
              <p>Select the class and subject you are conducting the lecture for.</p>
            </div>
            <div className="step-item">
              <div className="step-number">2</div>
              <p>Enter the lecture date, topic, and the count of students present.</p>
            </div>
            <div className="step-item">
              <div className="step-number">3</div>
              <p><strong>Submit</strong> — the attendance percentage updates immediately in the tracking dashboard.</p>
            </div>
          </div>

          <div className="info-alert">
            <p><strong>Note:</strong> Submissions are time-stamped and immutable. Contact the HOD to correct an erroneous entry.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarkAttendance;
