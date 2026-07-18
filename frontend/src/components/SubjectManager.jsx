import React, { useState, useEffect } from 'react';
import { Plus, Trash2, BookOpen, Filter } from 'lucide-react';
import './SubjectManager.css';

const SubjectManager = ({ assignedClasses, availableClasses = [] }) => {
  const [subjects, setSubjects] = useState([]);
  const [mySubjects, setMySubjects] = useState([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [yearFilter, setYearFilter] = useState('');
  const [semesterFilter, setSemesterFilter] = useState('');

  // New Mapping State
  const [selectedSubjectId, setSelectedSubjectId] = useState('');
  const [selectedClassId, setSelectedClassId] = useState('');

  // Edit state
  const [editingSubjectId, setEditingSubjectId] = useState(null);
  const [editForm, setEditForm] = useState({
    code: '',
    name: '',
    year_level: 1,
    semester: 1,
    credits: 0,
    is_active: true,
  });
  const [editError, setEditError] = useState('');
  const [savingEdit, setSavingEdit] = useState(false);

  // Filter available classes to only those assigned to the faculty
  const myClasses = availableClasses.filter(c => {
    const currentClasses = (assignedClasses || '').replace(/[{}]/g, '').split(',').map(s => s.trim()).filter(s => s);
    return currentClasses.includes(c.name);
  });

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

  // ── Detect current semester parity from month ──
  const getCurrentSemParity = () => {
    const month = new Date().getMonth(); // 0=Jan … 11=Dec
    // Jan-Jun (0-5) → Even semesters (Sem-II, IV, VI, VIII)
    // Jul-Dec (6-11) → Odd semesters (Sem-I, III, V, VII)
    return month >= 0 && month <= 5 ? 'even' : 'odd';
  };

  // Map year → [odd_sem, even_sem]
  const YEAR_SEMS = { FE: [1, 2], SE: [3, 4], TE: [5, 6], BE: [7, 8] };

  const getDefaultSem = (year) => {
    if (!year || !YEAR_SEMS[year]) return '';
    const [odd, even] = YEAR_SEMS[year];
    return getCurrentSemParity() === 'even' ? String(even) : String(odd);
  };

  useEffect(() => {
    // Auto-select year when only one year is assigned
    if (allowedYears.length === 1 && !yearFilter) {
      setYearFilter(allowedYears[0]);
    }
  }, [allowedYears.join()]);

  useEffect(() => {
    // When year is set (or changes), auto-set semester to current parity
    if (yearFilter) {
      setSemesterFilter(getDefaultSem(yearFilter));
    } else {
      setSemesterFilter('');
    }
  }, [yearFilter]);

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
      console.error('Error fetching my subjects', e);
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
        let filtered = data.filter(sub => allowedYears.includes(sub.year));
        if (yearFilter) filtered = filtered.filter(sub => sub.year === yearFilter);
        if (semesterFilter) filtered = filtered.filter(sub => String(sub.semester) === String(semesterFilter));
        setSubjects(filtered);
      }
    } catch (e) {
      console.error('Error fetching subjects', e);
    } finally {
      setLoading(false);
    }
  };

  const handleMapSubject = async () => {
    if (!selectedSubjectId || !selectedClassId) return;
    const token = localStorage.getItem('accessToken');
    try {
      const res = await fetch(`/api/subjects/faculty/map/${selectedSubjectId}?class_id=${selectedClassId}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        fetchMySubjects();
        setSelectedSubjectId('');
      } else {
        alert('Failed to map subject. You may have already mapped it.');
      }
    } catch (e) {
      alert('Error mapping subject');
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
      alert('Error unmapping subject');
    }
  };

  const handleEditSubject = (subject) => {
    setEditingSubjectId(subject.id);
    setEditError('');
    setEditForm({
      code: subject.code,
      name: subject.name,
      year_level: subject.year_level,
      semester: subject.semester,
      credits: subject.credits,
      is_active: subject.is_active,
    });
  };

  const handleEditSubmit = async (event) => {
    event.preventDefault();
    setSavingEdit(true);
    setEditError('');

    const token = localStorage.getItem('accessToken');
    try {
      const res = await fetch(`/api/subjects/${editingSubjectId}`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(editForm),
      });

      if (!res.ok) {
        let message = 'Failed to update subject.';
        try {
          const data = await res.json();
          message = data?.detail || data?.message || message;
        } catch (e) {
          console.error('Error parsing patch response', e);
        }
        setEditError(message);
        return;
      }

      await fetchMySubjects();
      await fetchAllSubjects();
      setEditingSubjectId(null);
      setEditError('');
    } catch (e) {
      console.error('Error updating subject', e);
      setEditError('Error updating subject');
    } finally {
      setSavingEdit(false);
    }
  };

  const getAvailableSemesters = () => {
    let yearsToCheck = yearFilter ? [yearFilter] : allowedYears;
    let sems = [];
    if (yearsToCheck.includes('FE')) sems.push(1, 2);
    if (yearsToCheck.includes('SE')) sems.push(3, 4);
    if (yearsToCheck.includes('TE')) sems.push(5, 6);
    if (yearsToCheck.includes('BE')) sems.push(7, 8);
    return sems.sort((a, b) => a - b);
  };

  const availableSemesters = getAvailableSemesters();

  useEffect(() => {
    if (semesterFilter && !availableSemesters.includes(Number(semesterFilter))) {
      setSemesterFilter(yearFilter ? getDefaultSem(yearFilter) : '');
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
                <div className="subject-card-main">
                  <div className="subject-card-header">
                    <strong>{sub.name}</strong>
                    <span className="subject-code">{sub.code}</span>
                  </div>
                  <div className="badge-container">
                    <span className="badge">{sub.year} - Sem {sub.semester}</span>
                    <span className={`badge sem ${sub.is_active ? 'active' : 'inactive'}`}>
                      {sub.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  {editingSubjectId === sub.id && (
                    <form className="subject-edit-form" onSubmit={handleEditSubmit}>
                      <div className="edit-grid">
                        <label>
                          Code
                          <input
                            value={editForm.code}
                            onChange={(e) => setEditForm({ ...editForm, code: e.target.value })}
                            required
                          />
                        </label>
                        <label>
                          Name
                          <input
                            value={editForm.name}
                            onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                            required
                          />
                        </label>
                        <label>
                          Programme Year
                          <select
                            value={editForm.year_level}
                            onChange={(e) => setEditForm({ ...editForm, year_level: Number(e.target.value) })}
                          >
                            <option value={1}>FE</option>
                            <option value={2}>SE</option>
                            <option value={3}>TE</option>
                            <option value={4}>BE</option>
                          </select>
                        </label>
                        <label>
                          Semester
                          <input
                            type="number"
                            min="1"
                            max="8"
                            value={editForm.semester}
                            onChange={(e) => setEditForm({ ...editForm, semester: Number(e.target.value) })}
                            required
                          />
                        </label>
                        <label>
                          Credits
                          <input
                            type="number"
                            min="0"
                            value={editForm.credits}
                            onChange={(e) => setEditForm({ ...editForm, credits: Number(e.target.value) })}
                            required
                          />
                        </label>
                        <label className="checkbox-label">
                          <input
                            type="checkbox"
                            checked={editForm.is_active}
                            onChange={(e) => setEditForm({ ...editForm, is_active: e.target.checked })}
                          />
                          Active
                        </label>
                      </div>
                      {editError && <p className="edit-error">{editError}</p>}
                      <div className="edit-form-actions">
                        <button type="submit" className="btn-save" disabled={savingEdit}>
                          {savingEdit ? 'Saving...' : 'Save'}
                        </button>
                        <button
                          type="button"
                          className="btn-cancel"
                          onClick={() => {
                            setEditingSubjectId(null);
                            setEditError('');
                          }}
                        >
                          Cancel
                        </button>
                      </div>
                    </form>
                  )}
                </div>
                <div className="subject-card-actions">
                  <button onClick={() => handleEditSubject(sub)} className="btn-edit" title="Edit Subject">
                    Edit
                  </button>
                  <button onClick={() => handleUnmapSubject(sub.id)} className="btn-remove" title="Remove Subject">
                    <Trash2 size={16} />
                  </button>
                </div>
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
              value={selectedClassId}
              onChange={(e) => setSelectedClassId(e.target.value)}
              className="subject-select"
              style={{ flex: '0.5' }}
            >
              <option value="">-- Select a Class --</option>
              {myClasses.map(cls => (
                <option key={cls.id} value={cls.id}>{cls.name}</option>
              ))}
            </select>

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
              disabled={!selectedSubjectId || !selectedClassId}
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
