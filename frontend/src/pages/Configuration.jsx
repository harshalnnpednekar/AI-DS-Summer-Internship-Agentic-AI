import React, { useState } from 'react';
import { Sliders, Send, Trash2, Clock, AlertTriangle, CheckCircle } from 'lucide-react';
import './Pages.css';
import './Configuration.css';

const Configuration = () => {
  const [config, setConfig] = useState(() => {
    const saved = localStorage.getItem('agentConfig');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        console.error("Failed to parse config", e);
      }
    }
    return {
      threshold: 75,
      autoGenerate: true,
      notifyParents: true,
      autoBroadcast: false,
      dailyTime: '09:00'
    };
  });
  const [isSaving, setIsSaving] = useState(false);
  const [showToast, setShowToast] = useState(false);

  const handleSave = () => {
    setIsSaving(true);
    // Simulate API call and save to localStorage
    setTimeout(() => {
      localStorage.setItem('agentConfig', JSON.stringify(config));
      setIsSaving(false);
      setShowToast(true);
      setTimeout(() => setShowToast(false), 3000);
    }, 800);
  };

  const handleChange = (key, value) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="page-container">
      <div className="page-header">

        <h1 className="page-title">Agent Configuration</h1>
        <p className="page-subtitle">Configure automated rules, thresholds, and notification settings for the department agent.</p>
      </div>

      <div className="settings-grid">
        {/* Attendance Rules */}
        <div className="card settings-card">
          <div className="settings-card-header">
            <Sliders size={20} className="text-secondary" />
            <h2>Attendance Rules</h2>
          </div>
          
          <div className="setting-item">
            <div className="setting-item-header">
              <h3>Defaulter Threshold (%)</h3>
              <p>Students below this percentage will be flagged as defaulters.</p>
            </div>
            <div className="setting-control-slider">
              <input 
                type="range" 
                min="0" max="100" 
                value={config.threshold} 
                onChange={(e) => handleChange('threshold', e.target.value)}
                className="range-slider" 
              />
              <span className="slider-value">{config.threshold}%</span>
            </div>
          </div>
          
          <div className="setting-item">
            <div className="setting-item-header">
              <h3>Auto-Generate Defaulter List</h3>
              <p>Generate defaulter list automatically each week</p>
            </div>
            <div className="setting-control">
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={config.autoGenerate}
                  onChange={(e) => handleChange('autoGenerate', e.target.checked)}
                />
                <span className="slider round"></span>
              </label>
            </div>
          </div>
          
          <div className="setting-item border-none">
            <div className="setting-item-header">
              <h3>Notify Parents / Guardians</h3>
              <p>Send notifications to parent contacts automatically</p>
            </div>
            <div className="setting-control">
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={config.notifyParents}
                  onChange={(e) => handleChange('notifyParents', e.target.checked)}
                />
                <span className="slider round"></span>
              </label>
            </div>
          </div>
        </div>

        {/* Broadcast Settings */}
        <div className="card settings-card">
          <div className="settings-card-header">
            <Send size={20} className="text-secondary" />
            <h2>Broadcast Settings</h2>
          </div>
          
          <div className="setting-item">
            <div className="setting-item-header">
              <h3>Auto-Broadcast on Generation</h3>
              <p>Broadcast defaulter list immediately after generation (skips HOD review)</p>
            </div>
            <div className="setting-control">
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={config.autoBroadcast}
                  onChange={(e) => handleChange('autoBroadcast', e.target.checked)}
                />
                <span className="slider round"></span>
              </label>
            </div>
          </div>
          
          <div className="setting-item">
            <div className="setting-item-header">
              <h3>Daily Broadcast Time</h3>
              <p>Scheduled time for daily deadline reminder broadcasts.</p>
            </div>
            <div className="setting-control">
              <div className="time-input" style={{ position: 'relative' }}>
                <input 
                  type="time" 
                  value={config.dailyTime}
                  onChange={(e) => handleChange('dailyTime', e.target.value)}
                  style={{
                    border: 'none',
                    background: 'transparent',
                    fontSize: '1rem',
                    color: 'var(--color-text-primary)',
                    fontFamily: 'inherit',
                    outline: 'none'
                  }}
                />
              </div>
            </div>
          </div>
          
          {config.autoBroadcast ? (
            <div className="warning-banner" style={{ backgroundColor: 'rgba(34, 197, 94, 0.1)', border: '1px solid rgba(34, 197, 94, 0.3)' }}>
              <CheckCircle size={18} style={{ color: 'var(--color-success)' }} />
              <p>Auto-broadcast is currently <strong style={{ color: 'var(--color-success)' }}>enabled</strong>. Defaulter lists will be sent out instantly without requiring HOD approval.</p>
            </div>
          ) : (
            <div className="warning-banner">
              <AlertTriangle size={18} className="text-warning" />
              <p>Auto-broadcast is currently <strong>disabled</strong>. All broadcasts require explicit HOD approval from the Defaulter Management page.</p>
            </div>
          )}
        </div>
      </div>

      {/* Data Management */}
      <div className="card settings-card data-management-card">
        <div className="settings-card-header text-danger">
          <Trash2 size={20} />
          <h2>Data Management</h2>
        </div>
        
        <div className="setting-item border-none" style={{ alignItems: 'center' }}>
          <div className="setting-item-header">
            <h3>Clear All Broadcast Logs</h3>
            <p>Permanently deletes all stored broadcast history. This action cannot be undone.</p>
          </div>
          <div className="setting-control">
            <button 
              className="btn btn-outline btn-danger-outline"
              onClick={async () => {
                if(window.confirm('Are you sure you want to clear all logs? This cannot be undone.')) {
                  try {
                    const token = localStorage.getItem('token');
                    const res = await fetch('/api/events/broadcast-logs', {
                      method: 'DELETE',
                      headers: { 'Authorization': `Bearer ${token}` }
                    });
                    if (res.ok) {
                      alert('Logs cleared successfully.');
                    } else {
                      alert('Failed to clear logs.');
                    }
                  } catch (e) {
                    alert('Error clearing logs.');
                  }
                }
              }}
            >
              Clear Logs
            </button>
          </div>
        </div>
      </div>
      
      <div className="form-actions">
        <button 
          className="btn btn-primary" 
          style={{ padding: '0.75rem 2rem' }}
          onClick={handleSave}
          disabled={isSaving}
        >
          {isSaving ? 'Saving...' : 'Save Configuration'}
        </button>
      </div>

      {showToast && (
        <div className="toast-notification">
          <CheckCircle size={20} />
          Configuration saved successfully!
        </div>
      )}
    </div>
  );
};

export default Configuration;
