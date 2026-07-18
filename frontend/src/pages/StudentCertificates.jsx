import React, { useState, useEffect } from 'react';
import { UploadCloud, Trash2, CheckCircle, Clock, XCircle, AlertCircle, Award } from 'lucide-react';
import './Pages.css';

const CATEGORIES = ['hackathon', 'workshop', 'competition', 'certification', 'other'];

const statusIcon = (status) => {
  if (status === 'approved') return <CheckCircle size={14} style={{ color: '#16a34a' }} />;
  if (status === 'rejected') return <XCircle size={14} style={{ color: '#dc2626' }} />;
  return <Clock size={14} style={{ color: '#d97706' }} />;
};

const statusLabel = (status) => {
  if (status === 'approved') return { label: 'Approved', bg: '#dcfce7', color: '#16a34a' };
  if (status === 'rejected') return { label: 'Rejected', bg: '#fee2e2', color: '#dc2626' };
  return { label: 'Pending', bg: '#fef3c7', color: '#d97706' };
};

const StudentCertificates = () => {
  const token = localStorage.getItem('accessToken');

  const [certificates, setCertificates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Upload form state
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    title: '',
    event_name: '',
    category: 'hackathon',
    issuing_body: '',
    date_achieved: '',
  });
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState('');

  const fetchCertificates = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/certificates/me', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (data.success) {
        setCertificates(data.data.certificates);
      } else {
        setError(data.error || 'Failed to load certificates.');
      }
    } catch {
      setError('Network error. Could not load certificates.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCertificates();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this certificate? This cannot be undone.')) return;
    try {
      const res = await fetch(`/api/certificates/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      if (data.success) {
        setCertificates((prev) => prev.filter((c) => c.id !== id));
      } else {
        alert(data.error || 'Could not delete certificate.');
      }
    } catch {
      alert('Network error.');
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    setUploadError('');
    setUploadSuccess('');

    if (!file) {
      setUploadError('Please select a file.');
      return;
    }

    setUploading(true);
    const fd = new FormData();
    fd.append('title', form.title);
    fd.append('event_name', form.event_name);
    fd.append('category', form.category);
    fd.append('issuing_body', form.issuing_body);
    fd.append('date_achieved', form.date_achieved);
    fd.append('file', file);

    try {
      const res = await fetch('/api/certificates/upload', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: fd,
      });
      const data = await res.json();
      if (data.success) {
        setUploadSuccess('Certificate uploaded successfully. Awaiting verification.');
        setForm({ title: '', event_name: '', category: 'hackathon', issuing_body: '', date_achieved: '' });
        setFile(null);
        setShowForm(false);
        fetchCertificates();
      } else {
        setUploadError(data.error || 'Upload failed.');
      }
    } catch {
      setUploadError('Network error during upload.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="page-container">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 className="page-title">My Certificates</h1>
          <p className="page-subtitle">Upload participation or achievement certificates for HOD verification.</p>
        </div>
        <button
          className="btn btn-primary"
          style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '4px' }}
          onClick={() => { setShowForm(!showForm); setUploadError(''); setUploadSuccess(''); }}
        >
          <UploadCloud size={16} />
          {showForm ? 'Cancel' : 'Upload Certificate'}
        </button>
      </div>

      {uploadSuccess && (
        <div style={{ background: '#dcfce7', color: '#16a34a', padding: '10px 14px', borderRadius: '8px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px' }}>
          <CheckCircle size={15} /> {uploadSuccess}
        </div>
      )}

      {showForm && (
        <div className="card" style={{ padding: '24px', marginBottom: '24px' }}>
          <h3 style={{ fontSize: '15px', fontWeight: '600', marginBottom: '16px', color: '#0f172a' }}>Upload New Certificate</h3>
          <form onSubmit={handleUpload} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '12px', fontWeight: '500', color: '#64748b' }}>Certificate Title</label>
              <input
                required
                type="text"
                placeholder="e.g. Best Project Award"
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                style={{ padding: '8px 12px', borderRadius: '7px', border: '1px solid #e2e8f0', fontSize: '13px', outline: 'none' }}
              />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '12px', fontWeight: '500', color: '#64748b' }}>Event / Competition Name</label>
              <input
                required
                type="text"
                placeholder="e.g. HackMIT 2025"
                value={form.event_name}
                onChange={(e) => setForm({ ...form, event_name: e.target.value })}
                style={{ padding: '8px 12px', borderRadius: '7px', border: '1px solid #e2e8f0', fontSize: '13px', outline: 'none' }}
              />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '12px', fontWeight: '500', color: '#64748b' }}>Category</label>
              <select
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
                style={{ padding: '8px 12px', borderRadius: '7px', border: '1px solid #e2e8f0', fontSize: '13px', outline: 'none', background: 'white' }}
              >
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
                ))}
              </select>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '12px', fontWeight: '500', color: '#64748b' }}>Issuing Body</label>
              <input
                required
                type="text"
                placeholder="e.g. IEEE, Coursera, NPTEL"
                value={form.issuing_body}
                onChange={(e) => setForm({ ...form, issuing_body: e.target.value })}
                style={{ padding: '8px 12px', borderRadius: '7px', border: '1px solid #e2e8f0', fontSize: '13px', outline: 'none' }}
              />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '12px', fontWeight: '500', color: '#64748b' }}>Date Achieved</label>
              <input
                required
                type="date"
                value={form.date_achieved}
                onChange={(e) => setForm({ ...form, date_achieved: e.target.value })}
                style={{ padding: '8px 12px', borderRadius: '7px', border: '1px solid #e2e8f0', fontSize: '13px', outline: 'none' }}
              />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '12px', fontWeight: '500', color: '#64748b' }}>File (PDF / JPG / PNG)</label>
              <input
                required
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={(e) => setFile(e.target.files[0] || null)}
                style={{ padding: '6px 12px', borderRadius: '7px', border: '1px solid #e2e8f0', fontSize: '13px' }}
              />
            </div>

            {uploadError && (
              <div style={{ gridColumn: '1 / -1', display: 'flex', alignItems: 'center', gap: '6px', color: '#dc2626', fontSize: '13px' }}>
                <AlertCircle size={14} /> {uploadError}
              </div>
            )}

            <div style={{ gridColumn: '1 / -1', display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                style={{ padding: '8px 18px', borderRadius: '7px', border: '1px solid #e2e8f0', background: 'white', fontSize: '13px', cursor: 'pointer' }}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={uploading}
                className="btn btn-primary"
                style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px' }}
              >
                <UploadCloud size={14} />
                {uploading ? 'Uploading...' : 'Submit'}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="card" style={{ padding: '0' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #f1f5f9', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Award size={18} style={{ color: '#64748b' }} />
          <h2 style={{ fontSize: '14px', fontWeight: '600', color: '#0f172a', margin: 0 }}>
            My Submitted Certificates ({certificates.length})
          </h2>
        </div>

        {loading ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#64748b', fontSize: '13px' }}>Loading...</div>
        ) : error ? (
          <div style={{ padding: '24px', textAlign: 'center', color: '#dc2626', fontSize: '13px' }}>{error}</div>
        ) : certificates.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8', fontSize: '13px' }}>
            No certificates uploaded yet. Click "Upload Certificate" to get started.
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
              <tr style={{ background: '#f8fafc' }}>
                {['Title', 'Event', 'Category', 'Issuing Body', 'Date', 'Status', ''].map((h) => (
                  <th key={h} style={{ padding: '10px 16px', textAlign: 'left', fontWeight: '600', color: '#64748b', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {certificates.map((cert, idx) => {
                const s = statusLabel(cert.verification_status);
                return (
                  <tr key={cert.id} style={{ borderTop: idx === 0 ? 'none' : '1px solid #f1f5f9' }}>
                    <td style={{ padding: '12px 16px', fontWeight: '500', color: '#0f172a' }}>{cert.title}</td>
                    <td style={{ padding: '12px 16px', color: '#475569' }}>{cert.event_name}</td>
                    <td style={{ padding: '12px 16px' }}>
                      <span style={{ padding: '2px 8px', borderRadius: '99px', background: '#f1f5f9', color: '#475569', fontSize: '11px', fontWeight: '500' }}>
                        {cert.category}
                      </span>
                    </td>
                    <td style={{ padding: '12px 16px', color: '#475569' }}>{cert.issuing_body}</td>
                    <td style={{ padding: '12px 16px', color: '#64748b' }}>{cert.date_achieved}</td>
                    <td style={{ padding: '12px 16px' }}>
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', padding: '3px 9px', borderRadius: '99px', background: s.bg, color: s.color, fontSize: '11px', fontWeight: '600' }}>
                        {statusIcon(cert.verification_status)} {s.label}
                      </span>
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      {cert.verification_status === 'pending' && (
                        <button
                          onClick={() => handleDelete(cert.id)}
                          title="Delete"
                          style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#94a3b8', display: 'flex', alignItems: 'center' }}
                          onMouseOver={(e) => e.currentTarget.style.color = '#dc2626'}
                          onMouseOut={(e) => e.currentTarget.style.color = '#94a3b8'}
                        >
                          <Trash2 size={15} />
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default StudentCertificates;
