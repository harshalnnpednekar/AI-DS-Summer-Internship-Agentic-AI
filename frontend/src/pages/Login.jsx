import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Cpu, CheckCircle, Eye, EyeOff, Lock } from 'lucide-react';
import './Login.css';

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = (e) => {
    e.preventDefault();
    navigate('/dashboard');
  };

  const setDemoAccount = (role) => {
    if (role === 'HOD') {
      setEmail('hod@vesit.edu');
      setPassword('hod@123');
    } else {
      setEmail('faculty@vesit.edu');
      setPassword('faculty@123');
    }
  };

  return (
    <div className="login-wrapper">
      <div className="login-card-container">
        {/* Left Branding Panel */}
        <div className="login-branding">
          <div className="branding-glass">
            <div className="branding-header">
              <div className="brand-logo-container">
                <img src="/VESIT LOGO.jpg" alt="VESIT Logo" className="brand-icon-image" />
              </div>
              <div className="brand-text-header">
                <h2>Vivekanand Education Society's Institute of Technology</h2>
                <p>Artificial Intelligence & Data Science Department</p>
              </div>
            </div>

            <div className="branding-content">
              <h1 className="hero-title">OmniSync</h1>
              <p className="hero-subtitle">
                A centralized, intelligent platform designed to streamline faculty workflows—from automated attendance tracking to real-time academic calendar synchronization.
              </p>

              <ul className="feature-list">
                <li>
                  <CheckCircle size={20} className="feature-icon" />
                  <span>Automated defaulter generation & instant broadcast</span>
                </li>
                <li>
                  <CheckCircle size={20} className="feature-icon" />
                  <span>Real-time, frictionless attendance tracking</span>
                </li>
                <li>
                  <CheckCircle size={20} className="feature-icon" />
                  <span>Smart academic calendar parsing with proactive alerts</span>
                </li>
              </ul>
            </div>

            <div className="branding-footer">
              Academic Year 2024-25 · Secure Faculty Portal
            </div>
          </div>
        </div>

        {/* Right Login Panel */}
        <div className="login-form-section">
          <div className="login-form-inner">
            <div className="form-header">
              <h2>Sign in to your account</h2>
              <p>Use your institutional email address.</p>
            </div>

            <form onSubmit={handleLogin} className="login-form">
              <div className="form-group">
                <label>Email Address</label>
                <input 
                  type="email" 
                  placeholder="alex.dev@techcorp.io" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required 
                />
              </div>

              <div className="form-group">
                <label>Password</label>
                <div className="password-input-wrapper">
                  <input 
                    type={showPassword ? "text" : "password"} 
                    placeholder="Enter your password" 
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required 
                  />
                  <button 
                    type="button" 
                    className="toggle-password"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>
              </div>

              <button type="submit" className="login-btn">
                <Lock size={16} /> Sign In Securely
              </button>
            </form>

            <div className="demo-accounts-wrapper">
              <div className="demo-accounts-divider">
                <span>DEMO ACCOUNTS</span>
              </div>
              
              <div className="demo-accounts-grid">
                <button type="button" className="demo-card" onClick={() => setDemoAccount('HOD')}>
                  <div className="demo-card-header">
                    <span className="demo-role">HOD <span className="demo-access">(Full Access)</span></span>
                    <span className="demo-badge badge-hod">HOD</span>
                  </div>
                  <div className="demo-card-hint">credential hint: hod@123</div>
                </button>
                
                <button type="button" className="demo-card" onClick={() => setDemoAccount('FACULTY')}>
                  <div className="demo-card-header">
                    <span className="demo-role">Dr. Priya Mehta <span className="demo-access">— SE-A</span></span>
                    <span className="demo-badge badge-faculty">FACULTY</span>
                  </div>
                  <div className="demo-card-hint">credential hint: faculty@123</div>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
