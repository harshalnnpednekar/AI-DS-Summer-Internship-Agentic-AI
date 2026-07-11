import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, Eye, EyeOff, Lock, UserPlus, AlertCircle } from 'lucide-react';
import './Login.css';

const Login = () => {
  const navigate = useNavigate();
  const [isLoginMode, setIsLoginMode] = useState(true);
  
  // Auth State
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [role, setRole] = useState('STUDENT');
  const [rollNumber, setRollNumber] = useState('');
  const [division, setDivision] = useState('SE-A');
  
  // UI State
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAuth = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const endpoint = isLoginMode ? '/api/auth/login' : '/api/auth/signup';
      
      let bodyData;
      let headers = {};
      
      if (isLoginMode) {
        bodyData = new URLSearchParams();
        bodyData.append('username', email);
        bodyData.append('password', password);
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
      } else {
        bodyData = JSON.stringify({
          email,
          password,
          first_name: firstName,
          last_name: lastName,
          role,
          department: "AI & DS",
          division: role === 'STUDENT' ? division : "SE-A",
          current_semester: "4",
          roll_number: role === 'STUDENT' ? rollNumber : undefined
        });
        headers['Content-Type'] = 'application/json';
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers,
        body: bodyData
      });
      
      const data = await response.json();
      
      if (data.success) {
        localStorage.setItem('accessToken', data.data.access_token);
        localStorage.setItem('userRole', data.data.user.role);
        localStorage.setItem('userName', `${data.data.user.first_name} ${data.data.user.last_name}`);
        localStorage.setItem('userInitials', (data.data.user.first_name[0] + data.data.user.last_name[0]).toUpperCase());
        localStorage.setItem('userDesc', data.data.user.role === 'STUDENT' ? 'Student' : (data.data.user.role === 'HOD' ? 'Head of Department' : 'Faculty'));
        
        navigate('/dashboard');
      } else {
        setError(data.error || 'Authentication failed');
      }
    } catch (err) {
      setError('Network error. Is the backend running on port 8000?');
    } finally {
      setLoading(false);
    }
  };

  const setDemoAccount = (demoRole) => {
    setIsLoginMode(true);
    if (demoRole === 'HOD') {
      setEmail('hod.aids@ves.ac.in');
      setPassword('hod@123');
    } else if (demoRole === 'STUDENT') {
      setEmail('student1@ves.ac.in');
      setPassword('student@123');
    } else {
      setEmail('priya.mehta@ves.ac.in');
      setPassword('faculty@123');
    }
    setError('');
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
          <div className="login-form-inner" style={{ maxHeight: '100%', overflowY: 'auto' }}>
            <div className="form-header">
              <h2>{isLoginMode ? 'Sign in to your account' : 'Create new account'}</h2>
              <p>{isLoginMode ? 'Use your institutional email address.' : 'Register with your institutional details.'}</p>
            </div>

            {error && (
              <div className="error-banner" style={{ background: '#fef2f2', color: '#b91c1c', padding: '10px', borderRadius: '6px', marginBottom: '15px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px' }}>
                <AlertCircle size={16} />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleAuth} className="login-form">
              {!isLoginMode && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                  <div className="form-group">
                    <label>First Name</label>
                    <input type="text" placeholder="John" value={firstName} onChange={(e) => setFirstName(e.target.value)} required />
                  </div>
                  <div className="form-group">
                    <label>Last Name</label>
                    <input type="text" placeholder="Doe" value={lastName} onChange={(e) => setLastName(e.target.value)} required />
                  </div>
                </div>
              )}

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

              {!isLoginMode && (
                <div className="form-group">
                  <label>Role</label>
                  <select value={role} onChange={(e) => setRole(e.target.value)} required style={{ width: '100%', padding: '10px 14px', borderRadius: '8px', border: '1px solid #e2e8f0', outline: 'none' }}>
                    <option value="STUDENT">Student</option>
                    <option value="FACULTY">Faculty</option>
                    <option value="HOD">HOD</option>
                  </select>
                </div>
              )}

              {!isLoginMode && role === 'STUDENT' && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                  <div className="form-group">
                    <label>Roll Number</label>
                    <input type="text" placeholder="e.g. 2021001" value={rollNumber} onChange={(e) => setRollNumber(e.target.value)} required />
                  </div>
                  <div className="form-group">
                    <label>Class</label>
                    <select value={division} onChange={(e) => setDivision(e.target.value)} required style={{ width: '100%', padding: '10px 14px', borderRadius: '8px', border: '1px solid #e2e8f0', outline: 'none' }}>
                      <option value="SE-A">SE-A</option>
                      <option value="TE-A">TE-A</option>
                      <option value="BE-A">BE-A</option>
                    </select>
                  </div>
                </div>
              )}

              <button type="submit" className="login-btn" disabled={loading}>
                {loading ? 'Processing...' : (
                  isLoginMode ? <><Lock size={16} /> Sign In Securely</> : <><UserPlus size={16} /> Create Account</>
                )}
              </button>
            </form>

            <div style={{ textAlign: 'center', marginTop: '15px', fontSize: '13px' }}>
              <button 
                type="button" 
                onClick={() => {
                  setIsLoginMode(!isLoginMode);
                  setError('');
                }}
                style={{ background: 'none', border: 'none', color: '#4f46e5', fontWeight: '500', cursor: 'pointer' }}
              >
                {isLoginMode ? "Don't have an account? Sign Up" : "Already have an account? Sign In"}
              </button>
            </div>

            {isLoginMode && (
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
                    <div className="demo-card-hint">hod.aids@ves.ac.in</div>
                  </button>
                  
                  <button type="button" className="demo-card" onClick={() => setDemoAccount('FACULTY')}>
                    <div className="demo-card-header">
                      <span className="demo-role">Dr. Priya Mehta <span className="demo-access">— SE-A</span></span>
                      <span className="demo-badge badge-faculty">FACULTY</span>
                    </div>
                    <div className="demo-card-hint">priya.mehta@ves.ac.in</div>
                  </button>

                  <button type="button" className="demo-card" onClick={() => setDemoAccount('STUDENT')} style={{gridColumn: '1 / -1'}}>
                    <div className="demo-card-header">
                      <span className="demo-role">Test Student <span className="demo-access">— SE-A</span></span>
                      <span className="demo-badge badge-student" style={{backgroundColor: '#e0e7ff', color: '#4338ca'}}>STUDENT</span>
                    </div>
                    <div className="demo-card-hint">student1@ves.ac.in</div>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
