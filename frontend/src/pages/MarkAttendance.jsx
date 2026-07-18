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
  const [startHour, setStartHour] = useState('10');
  const [startMin, setStartMin] = useState('00');
  const [startAmPm, setStartAmPm] = useState('AM');
  const [endHour, setEndHour] = useState('11');
  const [endMin, setEndMin] = useState('00');
  const [endAmPm, setEndAmPm] = useState('AM');
  const [sessionType, setSessionType] = useState('');
  const [semester, setSemester] = useState('');
  const [currentSemesterNum, setCurrentSemesterNum] = useState(null);
  
  const [selectedClass, setSelectedClass] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('');

  const [classes, setClasses] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [mappings, setMappings] = useState([]);
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
          let fetchedClasses = data.data.classes || [];
          const fetchedSubjects = data.data.subjects || [];

          // ── Filter classes to only the faculty's assigned ones ──
          const userRole = localStorage.getItem('userRole');
          if (userRole !== 'HOD') {
            // Fetch the current user profile to get assigned_classes
            try {
              const profileRes = await fetch('/api/auth/me', {
                headers: { 'Authorization': `Bearer ${token}` }
              });
              const profileData = await profileRes.json();
              if (profileData.success && profileData.data.assigned_classes) {
                // Parse "SE-A, TE-B" or "{SE-A,TE-B}" format
                const assignedStr = profileData.data.assigned_classes
                  .replace(/[{}]/g, '').toUpperCase();
                const assignedList = assignedStr
                  .split(',')
                  .map(s => s.trim())
                  .filter(Boolean);

                if (assignedList.length > 0) {
                  fetchedClasses = fetchedClasses.filter(c =>
                    assignedList.includes(c.name.toUpperCase())
                  );
                }
              }
            } catch (profileErr) {
              console.warn('Could not fetch profile for class filtering', profileErr);
            }
          }

          if (fetchedClasses.length === 0) {
            alert("Warning: You do not have any classes assigned to you. Please contact HOD to map classes to your profile.");
          }

          setClasses(fetchedClasses);
          setSubjects(fetchedSubjects);
          setMappings(data.data.mappings || []);
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


  useEffect(() => {
    if (totalStudents) {
      setStudentsPresent(Math.max(0, parseInt(totalStudents) - absentees.length));
    } else {
      setStudentsPresent('');
    }
  }, [totalStudents, absentees]);

  useEffect(() => {
    if (!selectedClass || !date || classes.length === 0) {
      setSemester('');
      setCurrentSemesterNum(null);
      return;
    }
    const cls = classes.find(c => c.id === selectedClass);
    if (!cls) return;
    
    const className = cls.name.toUpperCase();
    let year = 0;
    if (className.includes('FE') || className.includes('FIRST')) year = 1;
    else if (className.includes('SE') || className.includes('SECOND')) year = 2;
    else if (className.includes('TE') || className.includes('THIRD')) year = 3;
    else if (className.includes('BE') || className.includes('FOURTH')) year = 4;
    
    if (year === 0) {
      setSemester('');
      setCurrentSemesterNum(null);
      return;
    }
    
    const dateObj = new Date(date);
    const month = dateObj.getMonth();
    // Jan (0) to Jun (5) is Even Sem (2, 4, 6, 8)
    // Jul (6) to Dec (11) is Odd Sem (1, 3, 5, 7)
    const isEvenSem = month >= 0 && month <= 5;
    const semNumber = isEvenSem ? (year * 2) : (year * 2 - 1);
    
    const getOrdinal = (n) => {
      if (n === 1) return '1st';
      if (n === 2) return '2nd';
      if (n === 3) return '3rd';
      return n + 'th';
    };
    
    setSemester(`${getOrdinal(semNumber)} Semester`);
    setCurrentSemesterNum(semNumber);
  }, [selectedClass, date, classes]);

  const handleClassChange = (e) => {
    const val = e.target.value;
    setSelectedClass(val);
    setSelectedSubject('');
    const cls = classes.find(c => c.id === val);
    if (cls) setTotalStudents(cls.total_students);
  };



  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitError('');
    setSubmitSuccess('');
    
    try {
      const finalTimeSlot = `${startHour.padStart(2, '0')}:${startMin.padStart(2, '0')} ${startAmPm} - ${endHour.padStart(2, '0')}:${endMin.padStart(2, '0')} ${endAmPm}`;

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
          time_slot: finalTimeSlot,
          topic_covered: topic,
          total_students_enrolled: parseInt(totalStudents),
          students_present_count: parseInt(studentsPresent),
          absentee_roll_numbers: absentees,
          session_type: sessionType
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
        setDate(new Date().toISOString().split('T')[0]);
        setStartHour('10');
        setStartMin('00');
        setStartAmPm('AM');
        setEndHour('11');
        setEndMin('00');
        setEndAmPm('AM');
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
        if (totalStudents && parseInt(val, 10) > parseInt(totalStudents, 10)) {
          alert(`Roll number ${val} exceeds total enrolled students (${totalStudents}).`);
        } else {
          setAbsentees([...absentees, val]);
        }
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
                <select className="form-select" value={selectedSubject} onChange={(e) => setSelectedSubject(e.target.value)} required disabled={!selectedClass}>
                  <option value="" disabled hidden>
                    {!selectedClass ? 'Select a class first' : 'Select a subject'}
                  </option>
                  {selectedClass && currentSemesterNum !== null && (() => {
                    const filtered = subjects.filter(s => {
                      if (s.semester !== currentSemesterNum) return false;
                      const role = localStorage.getItem('userRole');
                      if (role !== 'HOD') {
                        return mappings.some(m => m.class_id === selectedClass && m.subject_id === s.id);
                      }
                      return true;
                    });
                    
                    if (filtered.length === 0) {
                      return <option disabled>No subjects mapped for this class</option>;
                    }
                    
                    return filtered.map(s => (
                      <option key={s.id} value={s.id}>{s.name} ({s.code})</option>
                    ));
                  })()}
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group half">
                <label>Lecture Date <span className="text-danger">*</span></label>
                <div className="input-with-icon">
                  <input type="date" className="form-input" value={date} onChange={(e) => setDate(e.target.value)} required />
                </div>
              </div>
              <div className="form-group half time-slot-container">
                <label>Time Slot</label>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', width: '100%' }}>
                  {/* Start Time */}
                  <div style={{ flex: 1, display: 'flex', border: '1px solid #cbd5e1', borderRadius: '8px', overflow: 'hidden', background: '#ffffff', alignItems: 'center', boxShadow: 'inset 0 1px 2px rgba(0, 0, 0, 0.05)', height: '42px', justifyContent: 'center' }}>
                    <input type="text" maxLength={2} value={startHour} onChange={(e) => setStartHour(e.target.value.replace(/\D/g, ''))} style={{ flex: 1, width: '100%', textAlign: 'center', border: 'none', background: 'transparent', outline: 'none', fontSize: '15px', color: '#1e293b', fontWeight: '500' }} />
                    <span style={{ color: '#94a3b8', fontWeight: 'bold' }}>:</span>
                    <input type="text" maxLength={2} value={startMin} onChange={(e) => setStartMin(e.target.value.replace(/\D/g, ''))} style={{ flex: 1, width: '100%', textAlign: 'center', border: 'none', background: 'transparent', outline: 'none', fontSize: '15px', color: '#1e293b', fontWeight: '500' }} />
                    <select value={startAmPm} onChange={(e) => setStartAmPm(e.target.value)} style={{ flex: 1, width: '100%', border: 'none', borderLeft: '1px solid #e2e8f0', padding: '0 5px', background: '#f8fafc', outline: 'none', cursor: 'pointer', height: '100%', fontSize: '14px', color: '#475569', fontWeight: '600', textAlign: 'center' }}>
                      <option>AM</option>
                      <option>PM</option>
                    </select>
                  </div>
                  
                  <span style={{ color: '#64748b', fontWeight: 600 }}>to</span>
                  
                  {/* End Time */}
                  <div style={{ flex: 1, display: 'flex', border: '1px solid #cbd5e1', borderRadius: '8px', overflow: 'hidden', background: '#ffffff', alignItems: 'center', boxShadow: 'inset 0 1px 2px rgba(0, 0, 0, 0.05)', height: '42px', justifyContent: 'center' }}>
                    <input type="text" maxLength={2} value={endHour} onChange={(e) => setEndHour(e.target.value.replace(/\D/g, ''))} style={{ flex: 1, width: '100%', textAlign: 'center', border: 'none', background: 'transparent', outline: 'none', fontSize: '15px', color: '#1e293b', fontWeight: '500' }} />
                    <span style={{ color: '#94a3b8', fontWeight: 'bold' }}>:</span>
                    <input type="text" maxLength={2} value={endMin} onChange={(e) => setEndMin(e.target.value.replace(/\D/g, ''))} style={{ flex: 1, width: '100%', textAlign: 'center', border: 'none', background: 'transparent', outline: 'none', fontSize: '15px', color: '#1e293b', fontWeight: '500' }} />
                    <select value={endAmPm} onChange={(e) => setEndAmPm(e.target.value)} style={{ flex: 1, width: '100%', border: 'none', borderLeft: '1px solid #e2e8f0', padding: '0 5px', background: '#f8fafc', outline: 'none', cursor: 'pointer', height: '100%', fontSize: '14px', color: '#475569', fontWeight: '600', textAlign: 'center' }}>
                      <option>AM</option>
                      <option>PM</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group half">
                <label>Lecture Type <span className="text-danger">*</span></label>
                <select className="form-select" value={sessionType} onChange={(e) => setSessionType(e.target.value)} required>
                  <option value="" disabled hidden>Select lecture type</option>
                  <option value="Theory">Theory</option>
                  <option value="Practical">Practical</option>
                </select>
              </div>
              <div className="form-group half">
                <label>Semester</label>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="Auto-calculated" 
                  value={semester} 
                  readOnly
                  style={{ backgroundColor: '#f8fafc', color: '#64748b', cursor: 'not-allowed' }}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group" style={{ width: '100%' }}>
                <label>Lecture Topic / Module</label>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="Enter specific topic (Optional)" 
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                />
              </div>
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
                <label>Students Absent</label>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="Auto-calculated"
                  value={totalStudents ? absentees.length : ''}
                  readOnly
                  style={{ backgroundColor: '#f8fafc', color: '#64748b', cursor: 'not-allowed' }}
                />
              </div>
              <div className="form-group half">
                <label>Students Present <span className="text-danger">*</span></label>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="Auto-calculated" 
                  value={studentsPresent}
                  readOnly
                  style={{ backgroundColor: '#f8fafc', color: '#64748b', cursor: 'not-allowed' }}
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
              <p className="form-hint">Press comma or Enter to add a roll number.</p>
            </div>

            <div className="form-actions border-top">
              <button type="submit" className="btn btn-primary submit-btn">
                <Send size={16} /> Submit Attendance Record
              </button>
            </div>
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
              <p><strong>Class & Subject Allocation:</strong> Carefully select the specific class division and the corresponding subject you conducted. Note that the dropdowns will only display subjects that have been officially mapped to your faculty profile by the Head of Department. If a subject is missing, please contact the administration.</p>
            </div>
            <div className="step-item">
              <div className="step-number">2</div>
              <p><strong>Date & Time Slot Accuracy:</strong> Ensure the lecture date matches the actual day the session was conducted (it defaults to today). Input the exact time slot (e.g., 10:30 - 11:30) using the 24-hour format; the field will automatically space it for you. This precision is required for timetable audits.</p>
            </div>
            <div className="step-item">
              <div className="step-number">3</div>
              <p><strong>Lecture Details:</strong> Specify whether this was a Theory or Practical session, and provide a brief but descriptive title for the module or topic covered during the class.</p>
            </div>
            <div className="step-item">
              <div className="step-number">4</div>
              <p><strong>Student Count:</strong> Input the total number of students enrolled in the selected class. This number forms the baseline for calculating the overall attendance percentage.</p>
            </div>
            <div className="step-item">
              <div className="step-number">5</div>
              <p><strong>Record Absentees:</strong> Type the precise roll numbers of any absent students and press comma (,) or Enter to add them as tags. The system will automatically subtract this from the total enrolled to calculate the 'Present' count.</p>
            </div>
            <div className="step-item">
              <div className="step-number">6</div>
              <p><strong>Submit:</strong> Click submit to finalize the record. This action instantly updates departmental attendance metrics, tracking dashboards, and triggers real-time updates to any relevant defaulter lists across the platform.</p>
            </div>
          </div>

          {localStorage.getItem('userRole') !== 'HOD' && (
            <div className="info-alert">
              <p><strong>Note:</strong> Submissions are time-stamped and immutable. Contact the HOD to correct an erroneous entry.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MarkAttendance;
