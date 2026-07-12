import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Mail, Phone, Building2, Calendar,
  Award, Hash, Layers, Users, Edit3, Save, X, FileText
} from 'lucide-react';
import './Profile.css';

const getInitials = (first = '', last = '') =>
  `${first[0] || ''}${last[0] || ''}`.toUpperCase();

const Profile = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Edit mode state
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchProfile();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchProfile = async () => {
    const token = localStorage.getItem('accessToken');
    if (!token) { navigate('/login'); return; }
    try {
      const res = await fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      if (data.success) {
        setProfile(data.data);
        setEditForm(data.data);
      } else {
        setError(data.error || 'Failed to load profile');
      }
    } catch {
      setError('Network error — is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  const handleEditChange = (field, value) => {
    setEditForm(prev => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    setSaving(true);
    const token = localStorage.getItem('accessToken');
    try {
      const payload = {
        first_name: editForm.first_name,
        last_name: editForm.last_name,
        phone: editForm.phone,
        bio: editForm.bio,
        designation: editForm.designation,
        department: editForm.department,
        assigned_classes: editForm.assigned_classes,
      };

      const res = await fetch('/api/auth/me', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        setIsEditing(false);
        fetchProfile(); // refresh
      } else {
        alert(data.error || 'Failed to update profile');
      }
    } catch {
      alert('Network error while saving');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="profile-page" style={{display:'flex', justifyContent:'center', alignItems:'center', height:'100vh'}}>
        <span style={{color: '#64748b'}}>Loading profile...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="profile-page">
        <span style={{ color: '#ef4444' }}>{error}</span>
      </div>
    );
  }

  const role = profile.role || 'STUDENT';
  const fullName = `${profile.first_name} ${profile.last_name}`;
  const initials = getInitials(profile.first_name, profile.last_name);
  const memberSince = profile.created_at
    ? new Date(profile.created_at).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
    : 'N/A';

  return (
    <div className="profile-page">
      <div className="profile-header-container">
        <h1 className="profile-title">User Profile</h1>
        <div className="profile-actions">
          {isEditing ? (
            <>
              <button className="btn-cancel" onClick={() => { setIsEditing(false); setEditForm(profile); }} disabled={saving}>
                <X size={16} /> Cancel
              </button>
              <button className="btn-save" onClick={handleSave} disabled={saving}>
                <Save size={16} /> {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </>
          ) : (
            <button className="btn-edit" onClick={() => setIsEditing(true)}>
              <Edit3 size={16} /> Edit Profile
            </button>
          )}
        </div>
      </div>

      <div className="profile-content">
        {/* Left Sidebar (Avatar + Quick Info) */}
        <div className="profile-sidebar-card">
          <div className="profile-avatar-large">{initials}</div>
          <h2 className="profile-name">{fullName}</h2>
          <div className="profile-role-badge">
            {role === 'HOD' ? 'Head of Department' : role === 'FACULTY' ? 'Faculty Member' : 'Student'}
          </div>

          <div className="profile-quick-info">
            <div className="quick-info-item">
              <Mail size={16} /> {profile.email}
            </div>
            <div className="quick-info-item">
              <Phone size={16} /> {profile.phone || 'No phone provided'}
            </div>
            <div className="quick-info-item">
              <Calendar size={16} /> Joined {memberSince}
            </div>
          </div>
        </div>

        {/* Right Details Section */}
        <div className="profile-details-section">
          
          {/* Basic Details */}
          <div className="detail-card">
            <h3 className="detail-card-header">Personal Information</h3>
            {isEditing ? (
              <div className="detail-grid">
                <div className="detail-item">
                  <label className="detail-label">First Name</label>
                  <input className="form-input" value={editForm.first_name || ''} onChange={(e) => handleEditChange('first_name', e.target.value)} />
                </div>
                <div className="detail-item">
                  <label className="detail-label">Last Name</label>
                  <input className="form-input" value={editForm.last_name || ''} onChange={(e) => handleEditChange('last_name', e.target.value)} />
                </div>
                <div className="detail-item">
                  <label className="detail-label">Phone Number</label>
                  <input className="form-input" value={editForm.phone || ''} onChange={(e) => handleEditChange('phone', e.target.value)} />
                </div>
                <div className="detail-item" style={{ gridColumn: '1 / -1' }}>
                  <label className="detail-label">Bio / About</label>
                  <textarea className="form-textarea" value={editForm.bio || ''} onChange={(e) => handleEditChange('bio', e.target.value)} />
                </div>
              </div>
            ) : (
              <div className="detail-grid">
                <div className="detail-item">
                  <span className="detail-label">Full Name</span>
                  <span className="detail-value">{fullName}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Phone Number</span>
                  <span className="detail-value">{profile.phone || 'Not provided'}</span>
                </div>
                <div className="detail-item" style={{ gridColumn: '1 / -1' }}>
                  <span className="detail-label">Bio / About</span>
                  <span className="detail-value">{profile.bio || 'No bio provided.'}</span>
                </div>
              </div>
            )}
          </div>

          {/* Academic / Professional Details */}
          <div className="detail-card">
            <h3 className="detail-card-header">
              {role === 'STUDENT' ? 'Academic Details' : 'Professional Details'}
            </h3>
            
            <div className="detail-grid">
              <div className="detail-item">
                <span className="detail-label">Department</span>
                {isEditing ? (
                  <input className="form-input" value={editForm.department || ''} onChange={(e) => handleEditChange('department', e.target.value)} />
                ) : (
                  <span className="detail-value">{profile.department || 'N/A'}</span>
                )}
              </div>

              {(role === 'HOD' || role === 'FACULTY') && (
                <>
                  <div className="detail-item">
                    <span className="detail-label">Designation</span>
                    {isEditing ? (
                      <input className="form-input" value={editForm.designation || ''} onChange={(e) => handleEditChange('designation', e.target.value)} />
                    ) : (
                      <span className="detail-value">{profile.designation || 'N/A'}</span>
                    )}
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Assigned Classes</span>
                    {isEditing ? (
                      <input className="form-input" value={editForm.assigned_classes || ''} placeholder="e.g. SE-A, TE-B" onChange={(e) => handleEditChange('assigned_classes', e.target.value)} />
                    ) : (
                      <span className="detail-value">{profile.assigned_classes || 'None'}</span>
                    )}
                  </div>
                </>
              )}

              {role === 'STUDENT' && (
                <>
                  <div className="detail-item">
                    <span className="detail-label">Roll Number</span>
                    <span className="detail-value">{profile.roll_number || 'N/A'}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Semester</span>
                    <span className="detail-value">{profile.current_semester || 'N/A'}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Division / Class</span>
                    <span className="detail-value">{profile.division || 'N/A'}</span>
                  </div>
                </>
              )}
              
              <div className="detail-item">
                <span className="detail-label">Joining Year</span>
                <span className="detail-value">{profile.joining_year || 'N/A'}</span>
              </div>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  );
};

export default Profile;
