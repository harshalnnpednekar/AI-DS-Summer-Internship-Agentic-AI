import React, { useState, useEffect } from 'react';
import { Plus, Trash2, BookOpen, Filter } from 'lucide-react';
import './SubjectManager.css';

const SubjectManager = ({ assignedClasses }) => {
  const [subjects, setSubjects] = useState([]);
  const [mySubjects, setMySubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Filters
  const [yearFilter, setYearFilter] = useState('');
  const [semesterFilter, setSemesterFilter] = useState('');
  
  // New Mapping State
  const [selectedSubjectId, setSelectedSubjectId] = useState('');
  const [classId, setClassId] = useState(''); // Assuming a generic input or selection for class, though typically it's an ID. Let's just use a dummy UUID or fetch classes?

  // Mock class ID for now, since we haven't built class management fully
  const MOCK_CLASS_ID = "00000000-0000-0000-0000-000000000000";

  // Parse allowed years from assignedClasses
  const getAllowedYears = (classesStr) => {
    if (!classesStr) return [];
    const str = classesStr.toUpperCase();
    const years = new Set();
    if (str.includes('FE') || str.includes('FIRST')) years.add('FE');
    if (str.includes('SE') || str.includes('SECOND')) years.add('SE');
    if (str.includes('TE') || str.includes('THIRD')) years.add('TE');
    if (str.includes('BE') || str.includes('FOURTH')) years.add('BE');
    return Array.from(years);
  };

  const allowedYears = getAllowedYears(assignedClasses);

  useEffect(() => {
    fetchMySubjects();
    if (allowedYears.length > 0) {
      fetchAllSubjects();
    }
  }, [yearFilter, semesterFilter, assignedClasses]);

  const fetchMySubjects = async () => {
    const token = localStorage.getItem('accessToken');
    try {
      const res = await fetch('/api/subjects/faculty', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      if (Array.isArray(data)) {
        setMySubjects(data);
      }
    } catch (e) {
      console.error("Error fetching my subjects", e);
    }
  };

  const fetchAllSubjects = async () => {
    const token = localStorage.getItem('accessToken');
    let url = '/api/subjects?';
    if (yearFilter) url += `year=${yearFilter}&`;
    if (semesterFilter) url += `semester=${semesterFilter}`;
    
    try {
      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      if (Array.isArray(data)) {
        const filtered = data.filter(sub => allowedYears.includes(sub.year));
        setSubjects(filtered);
      }
    } catch (e) {
      console.error("Error fetching subjects", e);
    } finally {
      setLoading(false);
    }
  };

  const handleMapSubject = async () => {
    if (!selectedSubjectId) return;
    const token = localStorage.getItem('accessToken');
    try {
      const res = await fetch(`/api/subjects/faculty/map/${selectedSubjectId}?class_id=${MOCK_CLASS_ID}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        fetchMySubjects();
        setSelectedSubjectId('');
      } else {
        alert("Failed to map subject. You may have already mapped it.");
      }
    } catch (e) {
      alert("Error mapping subject");
    }
  };

  const handleUnmapSubject = async (subjectId) => {
    const token = localStorage.getItem('accessToken');
    try {
      const res = await fetch(`/api/subjects/faculty/map/${subjectId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        fetchMySubjects();
      }
    } catch (e) {
      alert("Error unmapping subject");
    }
  };

  const getAvailableSemesters = () => {
    let yearsToCheck = yearFilter ? [yearFilter] : allowedYears;
    let sems = [];
    if (yearsToCheck.includes('FE')) sems.push(1, 2);
    if (yearsToCheck.includes('SE')) sems.push(3, 4);
    if (yearsToCheck.includes('TE')) sems.push(5, 6);
    if (yearsToCheck.includes('BE')) sems.push(7, 8);
    return sems.sort((a,b) => a - b);
  };
  
  const availableSemesters = getAvailableSemesters();

  useEffect(() => {
    if (semesterFilter && !availableSemesters.includes(Number(semesterFilter))) {
      setSemesterFilter('');
    }
  }, [yearFilter, allowedYears]);

  return (
    <div className="subject-manager">
      <div className="subject-manager-header">
        <BookOpen size={20} className="icon" />
        <h3>My Subjects</h3>
      </div>
      
      <div className="my-subjects-list">
        {mySubjects.length === 0 ? (
          <p className="no-subjects">No subjects mapped yet.</p>
        ) : (
          <ul>
            {mySubjects.map(sub => (
              <li key={sub.id}>
                <div>
                  <strong>{sub.name}</strong> ({sub.code})
                  <span className="badge">{sub.year} - Sem {sub.semester}</span>
                </div>
                <button onClick={() => handleUnmapSubject(sub.id)} className="btn-remove" title="Remove Subject">
                  <Trash2 size={16} />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="add-subject-section">
        <h4>Add Subject to Profile</h4>
        
        <div className="filters">
          <div className="filter-group">
            <Filter size={14} />
            <select value={yearFilter} onChange={(e) => setYearFilter(e.target.value)}>
              <option value="">All Permitted Years</option>
              {allowedYears.includes('FE') && <option value="FE">First Year (FE)</option>}
              {allowedYears.includes('SE') && <option value="SE">Second Year (SE)</option>}
              {allowedYears.includes('TE') && <option value="TE">Third Year (TE)</option>}
              {allowedYears.includes('BE') && <option value="BE">Final Year (BE)</option>}
            </select>
          </div>
          
          <div className="filter-group">
            <Filter size={14} />
            <select value={semesterFilter} onChange={(e) => setSemesterFilter(e.target.value)}>
              <option value="">All Semesters</option>
              {availableSemesters.map(s => (
                <option key={s} value={s}>Semester {s}</option>
              ))}
            </select>
          </div>
        </div>

        {allowedYears.length === 0 ? (
          <div className="warning-box">
            Please update your <strong>Assigned Classes</strong> in your profile (e.g. "SE-A, TE-B") to be able to map subjects.
          </div>
        ) : (
          <div className="add-controls">
          <select 
            value={selectedSubjectId} 
            onChange={(e) => setSelectedSubjectId(e.target.value)}
            className="subject-select"
          >
            <option value="">-- Select a Subject --</option>
            {subjects.map(sub => (
              <option key={sub.id} value={sub.id}>
                {sub.name} ({sub.code}) - {sub.year}
              </option>
            ))}
          </select>
          
          <button 
            className="btn-add" 
            onClick={handleMapSubject}
            disabled={!selectedSubjectId}
          >
            <Plus size={16} /> Add Subject
          </button>
        </div>
        )}
      </div>
    </div>
  );
};

export default SubjectManager;
