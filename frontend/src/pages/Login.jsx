import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  CheckCircle, Eye, EyeOff, Lock, UserPlus, AlertCircle,
  User, Mail, Shield, BookOpen, ArrowRight, ArrowLeft, Sparkles,
  GraduationCap, Briefcase, Phone, Calendar, FileText, ChevronDown
} from 'lucide-react';
import './Login.css';

// ─────────────────────────────────────────────
// Step indicator component
// ─────────────────────────────────────────────
const StepIndicator = ({ currentStep, totalSteps, steps }) => (
  <div className="step-indicator">
    {steps.map((step, idx) => {
      const stepNum = idx + 1;
      const isCompleted = stepNum < currentStep;
      const isActive = stepNum === currentStep;
      return (
        <React.Fragment key={idx}>
          <div className={`step-dot-wrapper ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}>
            <div className="step-dot">
              {isCompleted ? <CheckCircle size={14} /> : <span>{stepNum}</span>}
            </div>
            <span className="step-label">{step.label}</span>
          </div>
          {idx < totalSteps - 1 && (
            <div className={`step-connector ${isCompleted ? 'completed' : ''}`} />
          )}
        </React.Fragment>
      );
    })}
  </div>
);

// ─────────────────────────────────────────────
// Main Login component
// ─────────────────────────────────────────────
const Login = () => {
  const navigate = useNavigate();
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [currentStep, setCurrentStep] = useState(1);

  // Auth State
  const [email, setEmail]         = useState('');
  const [password, setPassword]   = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName]   = useState('');
  const [role, setRole]           = useState('STUDENT');

  // Student fields
  const [rollNumber, setRollNumber]           = useState('');
  const [division, setDivision]               = useState('SE-A');
  const [currentSemester, setCurrentSemester] = useState('4');

  // Faculty / HOD fields
  const [designation, setDesignation]     = useState('');
  const [assignedClasses, setAssignedClasses] = useState('');
  const [joiningYear, setJoiningYear]     = useState('');

  // Common extra fields
  const [phone, setPhone] = useState('');
  const [bio, setBio]     = useState('');

  // UI State
  const [showPassword, setShowPassword]           = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError]   = useState('');
  const [loading, setLoading] = useState(false);
  const [animDir, setAnimDir] = useState('forward'); // 'forward' | 'backward'

  // ── STEP CONFIG ────────────────────────────
  const signupSteps = [
    { label: 'Identity',  icon: <User size={16} /> },
    { label: 'Security',  icon: <Shield size={16} /> },
    { label: 'Role',      icon: role === 'STUDENT' ? <GraduationCap size={16} /> : <Briefcase size={16} /> },
    { label: 'Profile',   icon: <FileText size={16} /> },
  ];
  const totalSteps = signupSteps.length;

  // ── Step Validation ────────────────────────
  const validateStep = () => {
    setError('');
    if (currentStep === 1) {
      if (!firstName.trim()) return setError('First name is required.'), false;
      if (!lastName.trim())  return setError('Last name is required.'), false;
      if (!email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))
        return setError('Enter a valid email address.'), false;
    }
    if (currentStep === 2) {
      if (password.length < 6) return setError('Password must be at least 6 characters.'), false;
      if (password !== confirmPassword) return setError('Passwords do not match.'), false;
    }
    if (currentStep === 3) {
      if (role === 'STUDENT') {
        if (!rollNumber.trim()) return setError('Roll number is required.'), false;
      }
    }
    return true;
  };

  const goNext = () => {
    if (!validateStep()) return;
    setAnimDir('forward');
    setCurrentStep(s => Math.min(s + 1, totalSteps));
  };

  const goPrev = () => {
    setError('');
    setAnimDir('backward');
    setCurrentStep(s => Math.max(s - 1, 1));
  };

  // ── Submit ─────────────────────────────────
  const handleSignup = async (e) => {
    e.preventDefault();
    if (!validateStep()) return;
    setLoading(true);
    try {
      const bodyData = JSON.stringify({
        email,
        password,
        first_name: firstName,
        last_name: lastName,
        role,
        department: 'AI & DS',
        phone: phone || undefined,
        bio: bio || undefined,
        joining_year: joiningYear || undefined,
        division: role === 'STUDENT' ? division : undefined,
        current_semester: role === 'STUDENT' ? currentSemester : undefined,
        roll_number: role === 'STUDENT' ? rollNumber : undefined,
        designation: (role === 'FACULTY' || role === 'HOD')
          ? (designation || (role === 'HOD' ? 'HOD' : 'Assistant Professor'))
          : undefined,
        assigned_classes: (role === 'FACULTY' || role === 'HOD')
          ? (assignedClasses || undefined)
          : undefined,
      });
      const response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: bodyData,
      });
      const data = await response.json();
      if (data.success) {
        localStorage.setItem('accessToken', data.data.access_token);
        localStorage.setItem('userRole', data.data.user.role);
        localStorage.setItem('userName', `${data.data.user.first_name} ${data.data.user.last_name}`);
        localStorage.setItem('userInitials', (data.data.user.first_name[0] + data.data.user.last_name[0]).toUpperCase());
        localStorage.setItem('userDesc', data.data.user.role === 'STUDENT' ? 'Student' : (data.data.user.role === 'HOD' ? 'Head of Department' : 'Faculty'));
        navigate(data.data.user.role === 'STUDENT' ? '/student-dashboard' : '/dashboard');
      } else {
        setError(data.error || 'Registration failed. Please try again.');
      }
    } catch {
      setError('Network error. Is the backend running on port 8000?');
    } finally {
      setLoading(false);
    }
  };

  // ── Login submit ───────────────────────────
  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const bodyData = new URLSearchParams();
      bodyData.append('username', email);
      bodyData.append('password', password);
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: bodyData,
      });
      const data = await response.json();
      if (data.success) {
        localStorage.setItem('accessToken', data.data.access_token);
        localStorage.setItem('userRole', data.data.user.role);
        localStorage.setItem('userName', `${data.data.user.first_name} ${data.data.user.last_name}`);
        localStorage.setItem('userInitials', (data.data.user.first_name[0] + data.data.user.last_name[0]).toUpperCase());
        localStorage.setItem('userDesc', data.data.user.role === 'STUDENT' ? 'Student' : (data.data.user.role === 'HOD' ? 'Head of Department' : 'Faculty'));
        navigate(data.data.user.role === 'STUDENT' ? '/student-dashboard' : '/dashboard');
      } else {
        setError(data.error || 'Authentication failed');
      }
    } catch {
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

  const switchToSignup = () => {
    setIsLoginMode(false);
    setCurrentStep(1);
    setError('');
    setPassword('');
    setConfirmPassword('');
  };

  const switchToLogin = () => {
    setIsLoginMode(true);
    setCurrentStep(1);
    setError('');
    setPassword('');
    setConfirmPassword('');
  };

  // ── Render step content ────────────────────
  const renderSignupStep = () => {
    switch (currentStep) {
      // ── STEP 1: Identity
      case 1:
        return (
          <div className="signup-step" key="step1">
            <div className="step-hero">
              <div className="step-hero-icon"><User size={22} /></div>
              <div>
                <h3 className="step-title">Who are you?</h3>
                <p className="step-desc">Start with your full name and institutional email.</p>
              </div>
            </div>
            <div className="form-row-2">
              <div className="form-group">
                <label>First Name <span className="req">*</span></label>
                <input type="text" placeholder="Riya" value={firstName} onChange={e => setFirstName(e.target.value)} autoFocus />
              </div>
              <div className="form-group">
                <label>Last Name <span className="req">*</span></label>
                <input type="text" placeholder="Sharma" value={lastName} onChange={e => setLastName(e.target.value)} />
              </div>
            </div>
            <div className="form-group">
              <label>Institutional Email <span className="req">*</span></label>
              <div className="input-icon-wrapper">
                <Mail size={16} className="input-icon" />
                <input type="email" placeholder="you@ves.ac.in" value={email} onChange={e => setEmail(e.target.value)} className="has-icon" />
              </div>
            </div>
          </div>
        );

      // ── STEP 2: Security
      case 2:
        return (
          <div className="signup-step" key="step2">
            <div className="step-hero">
              <div className="step-hero-icon"><Shield size={22} /></div>
              <div>
                <h3 className="step-title">Secure your account</h3>
                <p className="step-desc">Choose a strong password — at least 6 characters.</p>
              </div>
            </div>
            <div className="form-group">
              <label>Password <span className="req">*</span></label>
              <div className="password-input-wrapper">
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Create a strong password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  autoFocus
                />
                <button type="button" className="toggle-password" onClick={() => setShowPassword(p => !p)}>
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {password.length > 0 && (
                <div className="password-strength">
                  <div className={`strength-bar ${password.length >= 10 ? 'strong' : password.length >= 6 ? 'medium' : 'weak'}`} />
                  <span className="strength-label">
                    {password.length >= 10 ? '🟢 Strong' : password.length >= 6 ? '🟡 Medium' : '🔴 Too short'}
                  </span>
                </div>
              )}
            </div>
            <div className="form-group">
              <label>Confirm Password <span className="req">*</span></label>
              <div className="password-input-wrapper">
                <input
                  type={showConfirmPassword ? 'text' : 'password'}
                  placeholder="Re-enter your password"
                  value={confirmPassword}
                  onChange={e => setConfirmPassword(e.target.value)}
                />
                <button type="button" className="toggle-password" onClick={() => setShowConfirmPassword(p => !p)}>
                  {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {confirmPassword.length > 0 && (
                <span className={`match-hint ${password === confirmPassword ? 'match' : 'no-match'}`}>
                  {password === confirmPassword ? '✓ Passwords match' : '✗ Passwords do not match'}
                </span>
              )}
            </div>
          </div>
        );

      // ── STEP 3: Role
      case 3:
        return (
          <div className="signup-step" key="step3">
            <div className="step-hero">
              <div className="step-hero-icon"><BookOpen size={22} /></div>
              <div>
                <h3 className="step-title">Your role at VESIT</h3>
                <p className="step-desc">Select your role and fill in the relevant details.</p>
              </div>
            </div>

            {/* Role Picker */}
            <div className="form-group">
              <label>I am a… <span className="req">*</span></label>
              <div className="role-selector">
                {['STUDENT', 'FACULTY', 'HOD'].map(r => (
                  <button
                    key={r}
                    type="button"
                    className={`role-pill ${role === r ? 'selected' : ''}`}
                    onClick={() => { setRole(r); setError(''); }}
                  >
                    {r === 'STUDENT' ? <GraduationCap size={15} /> : <Briefcase size={15} />}
                    {r === 'STUDENT' ? 'Student' : r === 'FACULTY' ? 'Faculty' : 'HOD'}
                  </button>
                ))}
              </div>
            </div>

            {/* Student fields */}
            {role === 'STUDENT' && (
              <>
                <div className="form-row-2">
                  <div className="form-group">
                    <label>Roll Number <span className="req">*</span></label>
                    <input type="text" placeholder="e.g. 2021001" value={rollNumber} onChange={e => setRollNumber(e.target.value)} autoFocus />
                  </div>
                  <div className="form-group">
                    <label>Class / Division</label>
                    <div className="select-wrapper">
                      <select value={division} onChange={e => setDivision(e.target.value)}>
                        <option value="SE-A">SE-A (2nd Year)</option>
                        <option value="TE-A">TE-A (3rd Year)</option>
                        <option value="BE-A">BE-A (4th Year)</option>
                      </select>
                      <ChevronDown size={16} className="select-icon" />
                    </div>
                  </div>
                </div>
                <div className="form-group">
                  <label>Current Semester</label>
                  <div className="select-wrapper">
                    <select value={currentSemester} onChange={e => setCurrentSemester(e.target.value)}>
                      {['1','2','3','4','5','6','7','8'].map(s => (
                        <option key={s} value={s}>Semester {s}</option>
                      ))}
                    </select>
                    <ChevronDown size={16} className="select-icon" />
                  </div>
                </div>
              </>
            )}

            {/* Faculty / HOD fields */}
            {(role === 'FACULTY' || role === 'HOD') && (
              <>
                <div className="form-group">
                  <label>Designation</label>
                  <input
                    type="text"
                    placeholder={role === 'HOD' ? 'Head of Department' : 'e.g. Assistant Professor'}
                    value={designation}
                    onChange={e => setDesignation(e.target.value)}
                    autoFocus
                  />
                </div>
                <div className="form-group">
                  <label>Assigned Classes <span className="hint-label">(comma-separated)</span></label>
                  <input type="text" placeholder="SE-A, TE-A" value={assignedClasses} onChange={e => setAssignedClasses(e.target.value)} />
                </div>
              </>
            )}
          </div>
        );

      // ── STEP 4: Profile
      case 4:
        return (
          <div className="signup-step" key="step4">
            <div className="step-hero">
              <div className="step-hero-icon"><Sparkles size={22} /></div>
              <div>
                <h3 className="step-title">Final touches</h3>
                <p className="step-desc">Add optional contact info and a short bio.</p>
              </div>
            </div>
            <div className="form-row-2">
              <div className="form-group">
                <label>Phone Number <span className="hint-label">(optional)</span></label>
                <div className="input-icon-wrapper">
                  <Phone size={15} className="input-icon" />
                  <input type="tel" placeholder="+91 98765 43210" value={phone} onChange={e => setPhone(e.target.value)} className="has-icon" autoFocus />
                </div>
              </div>
              <div className="form-group">
                <label>Joining Year <span className="hint-label">(optional)</span></label>
                <div className="input-icon-wrapper">
                  <Calendar size={15} className="input-icon" />
                  <input type="text" placeholder={new Date().getFullYear().toString()} value={joiningYear} onChange={e => setJoiningYear(e.target.value)} className="has-icon" />
                </div>
              </div>
            </div>
            <div className="form-group">
              <label>Short Bio <span className="hint-label">(optional)</span></label>
              <textarea
                placeholder="Tell us a bit about yourself…"
                value={bio}
                onChange={e => setBio(e.target.value)}
                rows={3}
                className="signup-textarea"
              />
            </div>

            {/* Review summary */}
            <div className="review-card">
              <div className="review-title">Account Summary</div>
              <div className="review-row"><span>Name</span><strong>{firstName} {lastName}</strong></div>
              <div className="review-row"><span>Email</span><strong>{email}</strong></div>
              <div className="review-row"><span>Role</span><strong>{role}</strong></div>
              {role === 'STUDENT' && <div className="review-row"><span>Division</span><strong>{division} — Sem {currentSemester}</strong></div>}
              {(role === 'FACULTY' || role === 'HOD') && designation && <div className="review-row"><span>Designation</span><strong>{designation}</strong></div>}
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  // ─────────────────────────────────────────────
  // RENDER
  // ─────────────────────────────────────────────
  return (
    <div className="login-wrapper">
      <div className="login-card-container">

        {/* ── Left Branding Panel ── */}
        <div className="login-branding">
          <div className="branding-glass">
            <div className="branding-header">
              <div className="brand-logo-container">
                <img src="/VESIT LOGO.jpg" alt="VESIT Logo" className="brand-icon-image" />
              </div>
              <div className="brand-text-header">
                <h2>Vivekanand Education Society's Institute of Technology</h2>
                <p>Artificial Intelligence &amp; Data Science Department</p>
              </div>
            </div>

            <div className="branding-content">
              <h1 className="hero-title">OmniSync</h1>
              <p className="hero-subtitle">
                A centralized, intelligent platform designed to streamline faculty workflows—from
                automated attendance tracking to real-time academic calendar synchronization.
              </p>
              <ul className="feature-list">
                <li><CheckCircle size={20} className="feature-icon" /><span>Automated defaulter generation &amp; instant broadcast</span></li>
                <li><CheckCircle size={20} className="feature-icon" /><span>Real-time, frictionless attendance tracking</span></li>
                <li><CheckCircle size={20} className="feature-icon" /><span>Smart academic calendar parsing with proactive alerts</span></li>
              </ul>
            </div>

            <div className="branding-footer" />
          </div>
        </div>

        {/* ── Right Panel ── */}
        <div className="login-form-section">
          <div className="login-form-inner">

            {/* ── LOGIN MODE ── */}
            {isLoginMode ? (
              <>
                <div className="form-header">
                  <h2>Sign in to your account</h2>
                  <p>Use your institutional email address.</p>
                </div>

                {error && (
                  <div className="error-banner">
                    <AlertCircle size={16} />
                    <span>{error}</span>
                  </div>
                )}

                <form onSubmit={handleLogin} className="login-form">
                  <div className="form-group">
                    <label>Email Address</label>
                    <div className="input-icon-wrapper">
                      <Mail size={16} className="input-icon" />
                      <input type="email" placeholder="you@ves.ac.in" value={email} onChange={e => setEmail(e.target.value)} required className="has-icon" />
                    </div>
                  </div>
                  <div className="form-group">
                    <label>Password</label>
                    <div className="password-input-wrapper">
                      <input type={showPassword ? 'text' : 'password'} placeholder="Enter your password" value={password} onChange={e => setPassword(e.target.value)} required />
                      <button type="button" className="toggle-password" onClick={() => setShowPassword(p => !p)}>
                        {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                      </button>
                    </div>
                  </div>
                  <button type="submit" className="login-btn" disabled={loading}>
                    {loading ? <span className="btn-spinner" /> : <><Lock size={16} /> Sign In Securely</>}
                  </button>
                </form>

                <div className="mode-switch">
                  <span>Don't have an account?</span>
                  <button type="button" onClick={switchToSignup}>Create Account →</button>
                </div>

                {/* Demo accounts */}
                <div className="demo-accounts-wrapper">
                  <div className="demo-accounts-divider"><span>DEMO ACCOUNTS</span></div>
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
                    <button type="button" className="demo-card" onClick={() => setDemoAccount('STUDENT')} style={{ gridColumn: '1 / -1' }}>
                      <div className="demo-card-header">
                        <span className="demo-role">Test Student <span className="demo-access">— SE-A</span></span>
                        <span className="demo-badge badge-student">STUDENT</span>
                      </div>
                      <div className="demo-card-hint">student1@ves.ac.in</div>
                    </button>
                  </div>
                </div>
              </>
            ) : (
              /* ── SIGNUP MODE (multi-step) ── */
              <>
                {/* Back arrow — step 1 → login, steps 2+ → previous step */}
                <button
                  type="button"
                  className="top-back-arrow"
                  onClick={() => currentStep === 1 ? switchToLogin() : goPrev()}
                  aria-label="Go back"
                >
                  <ArrowLeft size={18} />
                  <span>{currentStep === 1 ? 'Back to Sign In' : `Back to ${signupSteps[currentStep - 2].label}`}</span>
                </button>

                <div className="form-header signup-header">
                  <h2>Create new account</h2>
                  <p>Step {currentStep} of {totalSteps} — {signupSteps[currentStep - 1].label}</p>
                </div>

                {/* Step indicator */}
                <StepIndicator currentStep={currentStep} totalSteps={totalSteps} steps={signupSteps} />

                {error && (
                  <div className="error-banner">
                    <AlertCircle size={16} />
                    <span>{error}</span>
                  </div>
                )}

                {/* Step content wrapped in a form for keyboard Enter support */}
                <form
                  onSubmit={currentStep < totalSteps ? e => { e.preventDefault(); goNext(); } : handleSignup}
                  className="login-form"
                >
                  <div className={`step-slide ${animDir}`}>
                    {renderSignupStep()}
                  </div>

                  {/* Navigation — back button removed (handled by top-back-arrow above) */}
                  <div className="step-nav">

                    {currentStep < totalSteps ? (
                      <button type="submit" className="login-btn step-btn-next" disabled={loading}>
                        Continue <ArrowRight size={16} />
                      </button>
                    ) : (
                      <button type="submit" className="login-btn step-btn-next" disabled={loading}>
                        {loading ? <span className="btn-spinner" /> : <><UserPlus size={16} /> Create Account</>}
                      </button>
                    )}
                  </div>
                </form>

                <div className="mode-switch">
                  <span>Already have an account?</span>
                  <button type="button" onClick={switchToLogin}>Sign In →</button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
