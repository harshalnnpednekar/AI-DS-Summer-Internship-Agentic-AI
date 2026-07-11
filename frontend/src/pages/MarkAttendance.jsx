import React, { useState, useEffect } from 'react';
import { Edit2, Calendar, Send, Info, CheckCircle2 } from 'lucide-react';
import './Pages.css';
import './MarkAttendance.css';

const MarkAttendance = () => {
  const [topic, setTopic] = useState('');
  const [totalStudents, setTotalStudents] = useState('');
  const [studentsPresent, setStudentsPresent] = useState('');
  const [absentees, setAbsentees] = useState([]);
  const [currentRoll, setCurrentRoll] = useState('');
  const [date, setDate] = useState(() => new Date().toISOString().split('T')[0]);
  
  const [selectedClass, setSelectedClass] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('');

  const [classes, setClasses] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitSuccess, setSubmitSuccess] = useState('');
  const [submitError, setSubmitError] = useState('');

  useEffect(() => {
    const fetchFormMeta = async () => {
      try {
        const token = localStorage.getItem('accessToken');
        const response = await fetch('/api/attendance/form-meta', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        const data = await response.json();
        if (data.success) {
          const fetchedClasses = data.data.classes || [];
          const fetchedSubjects = data.data.subjects || [];
          
          if (fetchedClasses.length === 0) {
            alert("Warning: You do not have any classes or subjects assigned to you. Please contact HOD to map subjects to your profile.");
          }
          
          setClasses(fetchedClasses);
          setSubjects(fetchedSubjects);
        } else {
          console.error("API returned error:", data);
          alert("Could not load classes: " + (data.error || "Unknown error"));
        }
      } catch (err) {
        console.error("Failed to fetch meta", err);
        alert("Network error: Could not reach the backend to load classes. Please ensure the backend is running and you are logged in as Faculty/HOD.");
      } finally {
        setLoading(false);
      }
    };
    fetchFormMeta();
  }, []);

  const handleClassChange = (e) => {
    const val = e.target.value;
    setSelectedClass(val);
    const cls = classes.find(c => c.id === val);
    if (cls) setTotalStudents(cls.total_students);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitError('');
    setSubmitSuccess('');
    
    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch('/api/attendance/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          class_id: selectedClass,
          subject_id: selectedSubject,
          lecture_date: date,
          topic_covered: topic,
          total_students_enrolled: parseInt(totalStudents),
          students_present_count: parseInt(studentsPresent),
          absentee_roll_numbers: absentees
        })
      });
      const data = await response.json();
      if (data.success) {
        setSubmitSuccess("Attendance submitted successfully!");
        setTopic('');
        setTotalStudents('');
        setStudentsPresent('');
        setAbsentees([]);
        setCurrentRoll('');
        setDate('');
        setSelectedClass('');
        setSelectedSubject('');
      } else {
        setSubmitError(data.error || "Failed to submit attendance.");
      }
    } catch (err) {
      setSubmitError("Network error.");
    }
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
      setAbsentees(absentees.slice(0, -1));
    }
  };

  const removeAbsentee = (rollToRemove) => {
    setAbsentees(absentees.filter(roll => roll !== rollToRemove));
  };

  if (loading) {
    return <div className="page-container" style={{ padding: '2rem' }}>Loading form data...</div>;
  }

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

          {submitSuccess ? (
            <div className="success-state" style={{ textAlign: 'center', padding: '3rem 1rem' }}>
              <div style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: '64px', height: '64px', borderRadius: '50%', backgroundColor: '#dcfce7', color: '#10B981', marginBottom: '1.5rem' }}>
                <CheckCircle2 size={32} />
              </div>
              <h3 style={{ fontSize: '1.5rem', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '0.75rem' }}>Attendance Recorded Successfully</h3>
              <p style={{ color: 'var(--color-text-secondary)', marginBottom: '2rem', maxWidth: '400px', margin: '0 auto 2rem auto', lineHeight: '1.5' }}>
                The attendance for your lecture has been submitted. All statistics and dashboards have been dynamically updated.
              </p>
              <button 
                type="button"
                className="btn btn-primary" 
                onClick={() => setSubmitSuccess('')}
                style={{ padding: '0.75rem 1.5rem' }}
              >
                Submit Another Record
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="attendance-form">
              {submitError && (
                <div style={{ background: '#fee2e2', color: '#991b1b', padding: '10px', borderRadius: '6px', marginBottom: '15px' }}>
                  {submitError}
                </div>
              )}
            <div className="form-row">
              <div className="form-group half">
                <label>Class <span className="text-danger">*</span></label>
                <select className="form-select" value={selectedClass} onChange={handleClassChange} required>
                  <option value="" disabled hidden>Select a class</option>
                  {classes.map(c => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group half">
                <label>Subject <span className="text-danger">*</span></label>
                <select className="form-select" value={selectedSubject} onChange={(e) => setSelectedSubject(e.target.value)} required>
                  <option value="" disabled hidden>Select a subject</option>
                  {subjects.map(s => (
                    <option key={s.id} value={s.id}>{s.name} ({s.code})</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>Lecture Date <span className="text-danger">*</span></label>
              <div className="input-with-icon">
                <input type="date" className="form-input" value={date} onChange={(e) => setDate(e.target.value)} required />
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
                  max={totalStudents || 1000}
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
          )}
        </div>

        {/* Info Column */}
        <div className="card info-card">
          <h2 style={{ margin: '0 0 1.5rem 0', fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-text-primary)' }}>
            How It Works
          </h2>
          <div className="steps-list">
            <div className="step-item">
              <div className="step-number">1</div>
              <p>Select the class and subject you are conducting the lecture for. These are mapped dynamically to your profile.</p>
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
