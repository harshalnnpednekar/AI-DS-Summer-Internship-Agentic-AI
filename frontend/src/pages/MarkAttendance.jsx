import React, { useState } from 'react';
import { Edit2, Calendar, Send, Info } from 'lucide-react';
import './Pages.css';
import './MarkAttendance.css';

const MarkAttendance = () => {
  const [topic, setTopic] = useState('');
  const [totalStudents, setTotalStudents] = useState('');
  const [studentsPresent, setStudentsPresent] = useState('');
  const [absentees, setAbsentees] = useState([]);
  const [currentRoll, setCurrentRoll] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // form submission logic would go here
    setTopic('');
    setTotalStudents('');
    setStudentsPresent('');
    setAbsentees([]);
    setCurrentRoll('');
  };

  const handleRollKeyDown = (e) => {
    if (e.key === ',' || e.key === 'Enter') {
      e.preventDefault();
      const val = currentRoll.trim().replace(/,/g, '');
      if (val && !absentees.includes(val)) {
        setAbsentees([...absentees, val]);
      }
      setCurrentRoll('');
    } else if (e.key === 'Backspace' && !currentRoll && absentees.length > 0) {
      // Remove last tag if backspace is pressed on empty input
      setAbsentees(absentees.slice(0, -1));
    }
  };

  const removeAbsentee = (rollToRemove) => {
    setAbsentees(absentees.filter(roll => roll !== rollToRemove));
  };

  return (
    <div className="page-container">
      <div className="page-header">
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
            <div className="form-row">
              <div className="form-group half">
                <label>Class <span className="text-danger">*</span></label>
                <select className="form-select" defaultValue="" required>
                  <option value="" disabled>Select a class</option>
                  <option value="SE-A">SE-A (Second Year)</option>
                  <option value="SE-B">SE-B (Second Year)</option>
                  <option value="TE-A">TE-A (Third Year)</option>
                  <option value="TE-B">TE-B (Third Year)</option>
                  <option value="BE-A">BE-A (Final Year)</option>
                  <option value="BE-B">BE-B (Final Year)</option>
                </select>
              </div>
              <div className="form-group half">
                <label>Subject <span className="text-danger">*</span></label>
                <select className="form-select" defaultValue="" required>
                  <option value="" disabled>Select a subject</option>
                  <option value="DSA">Data Structures & Algorithms</option>
                  <option value="DBMS">Database Management Systems</option>
                  <option value="AI">Artificial Intelligence</option>
                  <option value="ML">Machine Learning</option>
                  <option value="CN">Computer Networks</option>
                  <option value="OS">Operating Systems</option>
                  <option value="DS">Data Science & Analytics</option>
                  <option value="DL">Deep Learning</option>
                  <option value="BDA">Big Data Analytics</option>
                  <option value="SE">Software Engineering</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>Lecture Date <span className="text-danger">*</span></label>
              <div className="input-with-icon">
                <input type="date" className="form-input" required />
                {/* Modern browsers show their own calendar icon, this is styled appropriately in CSS */}
              </div>
            </div>

            <div className="form-group">
              <label>Lecture Topic / Module <span className="text-danger">*</span></label>
              <input 
                type="text" 
                className="form-input" 
                placeholder="Enter the specific topic or module covered during the lecture" 
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
                  placeholder="Total enrolled students" 
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
                  placeholder="Number of attendees" 
                  min="0"
                  max={totalStudents || 100}
                  value={studentsPresent}
                  onChange={(e) => setStudentsPresent(e.target.value)}
                  required 
                />
              </div>
            </div>

            <div className="form-group">
              <label>Absentee Roll Numbers</label>
              <div className="tags-input-container form-input">
                {absentees.map(roll => (
                  <span key={roll} className="tag-pill">
                    {roll}
                    <button type="button" onClick={() => removeAbsentee(roll)}>&times;</button>
                  </span>
                ))}
                <input 
                  type="text" 
                  className="tag-input"
                  placeholder={absentees.length === 0 ? "Type roll number and press comma..." : ""} 
                  value={currentRoll}
                  onChange={(e) => setCurrentRoll(e.target.value)}
                  onKeyDown={handleRollKeyDown}
                />
              </div>
              <span className="hint-text" style={{ marginTop: '0.5rem', display: 'block' }}>Press comma or Enter to add a roll number.</span>
            </div>

            <button type="submit" className="btn btn-primary submit-btn">
              <Send size={16} /> Submit Attendance Record
            </button>
          </form>
        </div>

        {/* Info Column */}
        <div className="card info-card">
          <h2 style={{ margin: '0 0 1.5rem 0', fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-text-primary)' }}>
            How It Works
          </h2>
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
