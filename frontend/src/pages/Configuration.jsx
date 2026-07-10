import React from 'react';
import { Sliders, Send, Trash2, Clock, AlertTriangle } from 'lucide-react';
import './Pages.css';
import './Configuration.css';

const Configuration = () => {
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
              <input type="range" min="50" max="100" defaultValue="75" className="range-slider" />
              <span className="slider-value">75%</span>
            </div>
          </div>
          
          <div className="setting-item">
            <div className="setting-item-header">
              <h3>Auto-Generate Defaulter List</h3>
              <p>Generate defaulter list automatically each week</p>
            </div>
            <div className="setting-control">
              <label className="toggle-switch">
                <input type="checkbox" defaultChecked />
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
                <input type="checkbox" defaultChecked />
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
                <input type="checkbox" />
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
              <div className="time-input">
                <span>09:00</span>
                <Clock size={16} />
              </div>
            </div>
          </div>
          
          <div className="warning-banner">
            <AlertTriangle size={18} className="text-warning" />
            <p>Auto-broadcast is currently <strong>disabled</strong>. All broadcasts require explicit HOD approval from the Defaulter Management page.</p>
          </div>
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
            <button className="btn btn-outline btn-danger-outline">Clear Logs</button>
          </div>
        </div>
      </div>
      
      <div className="form-actions">
        <button className="btn btn-primary" style={{ padding: '0.75rem 2rem' }}>Save Configuration</button>
      </div>
    </div>
  );
};

export default Configuration;
