import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Cpu, CheckCircle, Eye, Lock } from 'lucide-react';
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
    <div className="login-container">
      {/* Left Branding Panel */}
      <div className="login-branding">
        <div className="branding-header">
          <div className="brand-logo-container">
            <Cpu size={24} color="var(--color-secondary)" />
          </div>
          <div className="brand-text-header">
            <h2>VESIT</h2>
            <p>AI & Data Science Department</p>
          </div>
        </div>

        <div className="branding-content">
          <h1 className="hero-title">Department<br />Management Agent</h1>
          <p className="hero-subtitle">
            A unified platform for automated attendance tracking, academic calendar management, and defaulter list generation — built for the AI & DS faculty.
          </p>

          <ul className="feature-list">
            <li>
              <CheckCircle size={20} className="feature-icon" />
              <span>Automated defaulter list generation & broadcast</span>
            </li>
            <li>
              <CheckCircle size={20} className="feature-icon" />
              <span>Real-time attendance tracking across all classes</span>
            </li>
            <li>
              <CheckCircle size={20} className="feature-icon" />
              <span>Academic calendar parsing & deadline alerts</span>
            </li>
          </ul>
        </div>

        <div className="branding-footer">
          Academic Year 2024-25 · Secure Faculty Portal
        </div>
      </div>

      {/* Right Login Panel */}
      <div className="login-form-section">
        <div className="login-form-container">
          <div className="form-header">
            <h2>Sign in to your account</h2>
            <p>Use your institutional email address.</p>
          </div>

          <form onSubmit={handleLogin} className="login-form">
            <div className="form-group">
              <label>Email Address</label>
              <input 
                type="email" 
                placeholder="you@vesit.edu" 
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
                  <Eye size={18} />
                </button>
              </div>
            </div>

            <button type="submit" className="btn btn-primary login-btn">
              <Lock size={16} /> Sign In Securely
            </button>
          </form>

          <div className="demo-accounts-divider">
            <span>DEMO ACCOUNTS</span>
          </div>

          <div className="demo-accounts-list">
            <button className="demo-account-btn" onClick={() => setDemoAccount('HOD')}>
              <div className="demo-account-info">
                <strong>HOD</strong> (Full Access)
              </div>
              <div className="demo-account-creds">
                <span className="demo-pwd">hod@123</span>
                <span className="badge badge-dark">HOD</span>
              </div>
            </button>
            
            <button className="demo-account-btn" onClick={() => setDemoAccount('FACULTY')}>
              <div className="demo-account-info">
                <strong>Dr. Priya Mehta</strong> — SE-A
              </div>
              <div className="demo-account-creds">
                <span className="demo-pwd">faculty@123</span>
                <span className="badge badge-outline-success">FACULTY</span>
              </div>
            </button>

            <button className="demo-account-btn" onClick={() => setDemoAccount('FACULTY')}>
              <div className="demo-account-info">
                <strong>Dr. Ananya Iyer</strong> — TE-A
              </div>
              <div className="demo-account-creds">
                <span className="demo-pwd">faculty@123</span>
                <span className="badge badge-outline-success">FACULTY</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
