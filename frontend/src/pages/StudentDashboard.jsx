import React, { useState, useEffect, useRef } from 'react';
import {
  GraduationCap, TrendingUp, BookOpen, AlertTriangle, CheckCircle2,
  Clock, Calendar, Bell, ChevronDown, ChevronUp, BarChart2,
  ShieldCheck, ShieldAlert, ShieldX, Info, Layers
} from 'lucide-react';
import './Pages.css';
import './StudentDashboard.css';

// ─── helpers ──────────────────────────────────────────────────────────────────
const getGreeting = () => {
  const h = new Date().getHours();
  if (h < 12) return 'Good morning';
  if (h < 17) return 'Good afternoon';
  return 'Good evening';
};

const getAcademicYear = () => {
  const now = new Date();
  const y = now.getFullYear();
  return now.getMonth() >= 5 ? `${y}-${(y + 1).toString().slice(2)}` : `${y - 1}-${y.toString().slice(2)}`;
};

// Circular progress gauge
const CircularGauge = ({ pct, size = 140, stroke = 12 }) => {
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (pct / 100) * circ;
  const color = pct >= 75 ? '#10B981' : pct >= 60 ? '#F59E0B' : '#EF4444';
  return (
    <svg width={size} height={size} className="gauge-svg">
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#E8EAED" strokeWidth={stroke} />
      <circle
        cx={size / 2} cy={size / 2} r={r} fill="none"
        stroke={color} strokeWidth={stroke}
        strokeDasharray={circ} strokeDashoffset={offset}
        strokeLinecap="round"
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
        style={{ transition: 'stroke-dashoffset 1s ease' }}
      />
      <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle"
        fontSize="22" fontWeight="700" fill={color}>{pct}%</text>
      <text x="50%" y="66%" textAnchor="middle" dominantBaseline="middle"
        fontSize="10" fill="#5F6368" fontWeight="500">OVERALL</text>
    </svg>
  );
};

// Mini bar for subject cards
const MiniBar = ({ pct, label }) => {
  const color = pct === null ? '#D1D5DB' : pct >= 75 ? '#10B981' : pct >= 60 ? '#F59E0B' : '#EF4444';
  return (
    <div className="mini-bar-row">
      <span className="mini-bar-label">{label}</span>
      {pct === null ? (
        <span className="mini-bar-na">N/A</span>
      ) : (
        <>
          <div className="mini-bar-track">
            <div className="mini-bar-fill" style={{ width: `${pct}%`, backgroundColor: color }} />
          </div>
          <span className="mini-bar-pct" style={{ color }}>{pct}%</span>
        </>
      )}
    </div>
  );
};

// Status icon for subject card
const StatusIcon = ({ status }) => {
  if (status === 'safe') return <ShieldCheck size={18} className="status-icon safe" />;
  if (status === 'at_risk') return <ShieldAlert size={18} className="status-icon at-risk" />;
  return <ShieldX size={18} className="status-icon critical" />;
};

// ─── Main Component ────────────────────────────────────────────────────────────
const StudentDashboard = () => {
  const token = localStorage.getItem('accessToken');
  const userName = localStorage.getItem('userName') || 'Student';

  const [attendance, setAttendance] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview'); // overview | subjects | timetable | alerts
  const [expandedSubject, setExpandedSubject] = useState(null);
  const animRef = useRef(false);

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);
      try {
        const [attRes, evtRes] = await Promise.all([
          fetch('/api/attendance/student/me', { headers: { Authorization: `Bearer ${token}` } }),
          fetch('/api/events/upcoming?days=30'),
        ]);
        const attData = await attRes.json();
        const evtData = await evtRes.json();

        if (attData.success) {
          setAttendance(attData.data);
        } else {
          setError(attData.error || 'Could not load attendance data.');
        }
        if (Array.isArray(evtData)) setEvents(evtData);
      } catch {
        setError('Network error. Please try again.');
      } finally {
        setLoading(false);
        animRef.current = true;
      }
    };
    fetchAll();
  }, [token]);

  // ── Loading ──────────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="sd-loading">
        <div className="sd-spinner" />
        <p>Loading your academic data…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="sd-error-state">
        <AlertTriangle size={40} />
        <h3>Could not load dashboard</h3>
        <p>{error}</p>
      </div>
    );
  }

  const att = attendance || {};
  const overall = att.overall_attendance ?? 0;
  const subjects = att.subject_wise || [];
  const recentLectures = att.recent_lectures || [];
  const isDefaulter = att.is_defaulter;
  const defaulterStatus = att.defaulter_status;

  const safeCount = subjects.filter(s => s.status === 'safe').length;
  const atRiskCount = subjects.filter(s => s.status === 'at_risk').length;
  const criticalCount = subjects.filter(s => s.status === 'critical').length;

  // Sort subjects: critical → at_risk → safe
  const sortedSubjects = [...subjects].sort((a, b) => {
    const order = { critical: 0, at_risk: 1, safe: 2 };
    return order[a.status] - order[b.status];
  });

  // Separate upcoming events within 7 days (alerts) vs rest
  const today = new Date();
  const urgentEvents = events.filter(e => {
    const diff = (new Date(e.date) - today) / 86400000;
    return diff >= 0 && diff <= 7;
  });
  const upcomingEvents = events.filter(e => new Date(e.date) >= today);

  return (
    <div className="page-container">
      {/* ── Page Header ───────────────────────────────────────────────────── */}
      <div className="page-header">
        <div className="sd-header-row">
          <div>
            <h1 className="page-title">{getGreeting()}, {userName.split(' ')[0]} 👋</h1>
            <p className="page-subtitle">
              Academic Year {getAcademicYear()} · {att.division || 'Student'} · Roll {att.roll_number || '—'}
            </p>
          </div>
          {isDefaulter && (
            <div className={`sd-defaulter-banner ${defaulterStatus === 'Critical' ? 'critical' : 'at-risk'}`}>
              <AlertTriangle size={16} />
              <span>{defaulterStatus} — Attendance below 75%</span>
            </div>
          )}
        </div>
      </div>

      {/* ── Tab Nav ───────────────────────────────────────────────────────── */}
      <div className="sd-tab-nav">
        {[
          { id: 'overview', label: 'Overview', icon: <BarChart2 size={16} /> },
          { id: 'subjects', label: 'Per-Subject', icon: <BookOpen size={16} /> },
          { id: 'timetable', label: 'Recent Lectures', icon: <Clock size={16} /> },
          { id: 'alerts', label: `Alerts ${urgentEvents.length > 0 ? `(${urgentEvents.length})` : ''}`, icon: <Bell size={16} /> },
        ].map(tab => (
          <button
            key={tab.id}
            className={`sd-tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.icon}
            <span>{tab.label}</span>
            {tab.id === 'alerts' && urgentEvents.length > 0 && (
              <span className="sd-alert-dot" />
            )}
          </button>
        ))}
      </div>

      {/* ══════════════ OVERVIEW TAB ══════════════════════════════════════════ */}
      {activeTab === 'overview' && (
        <>
          {/* KPI Row */}
          <div className="sd-kpi-grid">
            {/* Gauge Card */}
            <div className="card sd-gauge-card">
              <CircularGauge pct={overall} />
              <div className="sd-gauge-info">
                <h3>Overall Attendance</h3>
                <p className="sd-gauge-sub">
                  {att.attended_theory + att.attended_practical || 0} attended out of {att.total_theory + att.total_practical || 0} lectures
                </p>
                <div className="sd-gauge-pills">
                  <span className="gauge-pill theory">
                    <Layers size={12} /> Theory: {att.attended_theory}/{att.total_theory}
                  </span>
                  <span className="gauge-pill practical">
                    <Layers size={12} /> Practical: {att.attended_practical}/{att.total_practical}
                  </span>
                </div>
                {isDefaulter && (
                  <div className="sd-warning-note">
                    <Info size={13} />
                    <span>
                      You need to attend more lectures to reach the 75% threshold required by the department.
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Summary stats */}
            <div className="sd-summary-grid">
              <div className="card sd-stat-tile">
                <div className="sd-stat-icon" style={{ background: '#D1FAE5', color: '#10B981' }}>
                  <ShieldCheck size={20} />
                </div>
                <div className="sd-stat-num">{safeCount}</div>
                <div className="sd-stat-label">Safe Subjects</div>
                <div className="sd-stat-hint">≥ 75% attendance</div>
              </div>
              <div className="card sd-stat-tile">
                <div className="sd-stat-icon" style={{ background: '#FEF3C7', color: '#F59E0B' }}>
                  <ShieldAlert size={20} />
                </div>
                <div className="sd-stat-num">{atRiskCount}</div>
                <div className="sd-stat-label">At Risk</div>
                <div className="sd-stat-hint">60–74% attendance</div>
              </div>
              <div className="card sd-stat-tile">
                <div className="sd-stat-icon" style={{ background: '#FEE2E2', color: '#EF4444' }}>
                  <ShieldX size={20} />
                </div>
                <div className="sd-stat-num">{criticalCount}</div>
                <div className="sd-stat-label">Critical</div>
                <div className="sd-stat-hint">&lt; 60% attendance</div>
              </div>
              <div className="card sd-stat-tile">
                <div className="sd-stat-icon" style={{ background: '#DBEAFE', color: '#3B82F6' }}>
                  <BookOpen size={20} />
                </div>
                <div className="sd-stat-num">{subjects.length}</div>
                <div className="sd-stat-label">Total Subjects</div>
                <div className="sd-stat-hint">This semester</div>
              </div>
            </div>
          </div>

          {/* Quick Subject Overview */}
          {subjects.length > 0 && (
            <div className="card sd-quick-subjects">
              <div className="sd-section-header">
                <BarChart2 size={18} className="text-secondary" />
                <h2>Quick Attendance Overview</h2>
              </div>
              <div className="sd-quick-subject-list">
                {sortedSubjects.map((s, i) => (
                  <div key={i} className={`sd-quick-row status-${s.status}`}>
                    <div className="sd-quick-row-left">
                      <StatusIcon status={s.status} />
                      <div>
                        <div className="sd-quick-subject-name">{s.subject}</div>
                        <div className="sd-quick-faculty">{s.faculty}</div>
                      </div>
                    </div>
                    <div className="sd-quick-row-right">
                      <div className="sd-quick-bar-wrap">
                        <div className="sd-quick-bar-track">
                          <div
                            className="sd-quick-bar-fill"
                            style={{
                              width: `${s.attendance_pct}%`,
                              background: s.status === 'safe' ? '#10B981' : s.status === 'at_risk' ? '#F59E0B' : '#EF4444'
                            }}
                          />
                          <div className="sd-threshold-line" title="75% threshold" />
                        </div>
                        <span className={`sd-quick-pct ${s.status}`}>{s.attendance_pct}%</span>
                      </div>
                      {s.status !== 'safe' && s.lectures_needed > 0 && (
                        <span className="sd-lectures-needed">
                          +{s.lectures_needed} lec. to reach 75%
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              <div className="sd-threshold-legend">
                <div className="sd-threshold-line-sample" />
                <span>75% minimum threshold (departmental rule)</span>
              </div>
            </div>
          )}

          {subjects.length === 0 && (
            <div className="card sd-empty">
              <GraduationCap size={40} color="#5F6368" />
              <h3>No attendance data yet</h3>
              <p>Once your faculty mark lectures, your attendance will appear here.</p>
            </div>
          )}
        </>
      )}

      {/* ══════════════ PER-SUBJECT TAB ═══════════════════════════════════════ */}
      {activeTab === 'subjects' && (
        <div className="sd-subjects-grid">
          {sortedSubjects.length === 0 && (
            <div className="card sd-empty" style={{ gridColumn: '1/-1' }}>
              <BookOpen size={40} color="#5F6368" />
              <h3>No subject data yet</h3>
              <p>Attendance records will appear once lectures are conducted.</p>
            </div>
          )}
          {sortedSubjects.map((s, i) => {
            const isOpen = expandedSubject === i;
            return (
              <div key={i} className={`card sd-subject-card status-border-${s.status}`}>
                <div className="sd-subject-card-header" onClick={() => setExpandedSubject(isOpen ? null : i)}>
                  <div className="sd-subject-card-title">
                    <StatusIcon status={s.status} />
                    <div>
                      <div className="sd-subj-name">{s.subject}</div>
                      <div className="sd-subj-meta">
                        <span className="sd-subj-code">{s.code}</span>
                        <span className="sd-subj-dot">·</span>
                        <span>{s.faculty}</span>
                      </div>
                    </div>
                  </div>
                  <div className="sd-subject-card-right">
                    <span className={`sd-pct-badge ${s.status}`}>{s.attendance_pct}%</span>
                    {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                  </div>
                </div>

                {/* Always show bar */}
                <div className="sd-card-bar-wrap">
                  <div className="sd-card-bar-track">
                    <div
                      className="sd-card-bar-fill"
                      style={{
                        width: `${s.attendance_pct}%`,
                        background: s.status === 'safe' ? '#10B981' : s.status === 'at_risk' ? '#F59E0B' : '#EF4444'
                      }}
                    />
                    <div className="sd-card-threshold-line" title="75%" />
                  </div>
                  <span className="sd-card-bar-labels">
                    <span>0%</span><span>75%</span><span>100%</span>
                  </span>
                </div>

                {/* Expanded detail */}
                {isOpen && (
                  <div className="sd-subject-detail">
                    <div className="sd-detail-grid">
                      <div className="sd-detail-stat">
                        <div className="sd-detail-label">Attended</div>
                        <div className="sd-detail-val">{s.attended} / {s.total_lectures}</div>
                      </div>
                      <div className="sd-detail-stat">
                        <div className="sd-detail-label">Theory</div>
                        <div className="sd-detail-val">{s.total_theory > 0 ? `${s.theory_attendance}%` : 'N/A'}</div>
                      </div>
                      <div className="sd-detail-stat">
                        <div className="sd-detail-label">Practical</div>
                        <div className="sd-detail-val">{s.total_practical > 0 ? `${s.practical_attendance}%` : 'N/A'}</div>
                      </div>
                    </div>
                    <MiniBar pct={s.theory_attendance} label="Theory" />
                    <MiniBar pct={s.practical_attendance} label="Practical" />
                    {s.status !== 'safe' && (
                      <div className={`sd-subject-warning ${s.status}`}>
                        <AlertTriangle size={13} />
                        <span>
                          {s.status === 'critical'
                            ? `Critical: Only ${s.attendance_pct}% attendance. Immediate action required.`
                            : `At risk: Attend ${s.lectures_needed} more lecture(s) to reach the 75% threshold.`}
                        </span>
                      </div>
                    )}
                    {s.status === 'safe' && (
                      <div className="sd-subject-safe">
                        <CheckCircle2 size={13} />
                        <span>Compliant — You meet the 75% attendance requirement.</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* ══════════════ TIMETABLE / RECENT LECTURES TAB ═══════════════════════ */}
      {activeTab === 'timetable' && (
        <div className="card sd-timetable-card">
          <div className="sd-section-header" style={{ padding: '0 0 1rem 0' }}>
            <Clock size={18} className="text-secondary" />
            <h2>Recent Lecture Log</h2>
            <span className="count-badge">{recentLectures.length} records</span>
          </div>
          {recentLectures.length === 0 ? (
            <div className="sd-empty" style={{ padding: '3rem 0' }}>
              <Clock size={40} color="#5F6368" />
              <h3>No lecture records yet</h3>
              <p>Lectures will appear here once your faculty submit attendance.</p>
            </div>
          ) : (
            <div className="sd-timeline">
              {recentLectures.map((lec, i) => (
                <div key={i} className={`sd-timeline-item ${lec.present ? 'present' : 'absent'}`}>
                  <div className="sd-timeline-dot" />
                  <div className="sd-timeline-content">
                    <div className="sd-timeline-header-row">
                      <div>
                        <span className="sd-tl-subject">{lec.subject}</span>
                        <span className="sd-tl-type-badge">{lec.session_type}</span>
                      </div>
                      <span className={`sd-tl-status ${lec.present ? 'present' : 'absent'}`}>
                        {lec.present ? <><CheckCircle2 size={13} /> Present</> : <><AlertTriangle size={13} /> Absent</>}
                      </span>
                    </div>
                    <div className="sd-tl-meta">
                      <span><Calendar size={12} /> {lec.date}</span>
                      {lec.time_slot && <span><Clock size={12} /> {lec.time_slot}</span>}
                      <span>by {lec.faculty}</span>
                    </div>
                    {lec.topic && (
                      <div className="sd-tl-topic">Topic: {lec.topic}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ══════════════ ALERTS / EVENTS TAB ═══════════════════════════════════ */}
      {activeTab === 'alerts' && (
        <div className="sd-alerts-section">
          {urgentEvents.length > 0 && (
            <div className="card sd-urgent-events">
              <div className="sd-section-header" style={{ marginBottom: '1rem' }}>
                <Bell size={18} style={{ color: '#F59E0B' }} />
                <h2>Upcoming in 7 Days</h2>
                <span className="sd-urgent-badge">{urgentEvents.length}</span>
              </div>
              {urgentEvents.map((evt, i) => {
                const diff = Math.ceil((new Date(evt.date) - today) / 86400000);
                return (
                  <div key={i} className="sd-alert-card urgent">
                    <div className="sd-alert-date-block">
                      <div className="sd-alert-day">{new Date(evt.date).toLocaleDateString('en-IN', { day: 'numeric' })}</div>
                      <div className="sd-alert-month">{new Date(evt.date).toLocaleDateString('en-IN', { month: 'short' })}</div>
                    </div>
                    <div className="sd-alert-body">
                      <div className="sd-alert-title">{evt.title}</div>
                      {evt.description && <div className="sd-alert-desc">{evt.description}</div>}
                      <div className="sd-alert-meta">
                        {evt.department && <span className="sd-alert-tag">{evt.department}</span>}
                        {evt.audience && <span className="sd-alert-tag audience">{evt.audience}</span>}
                      </div>
                    </div>
                    <div className="sd-alert-countdown">
                      <span className={diff === 0 ? 'today' : diff <= 2 ? 'very-soon' : 'soon'}>
                        {diff === 0 ? 'Today' : `${diff}d`}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          <div className="card sd-all-events">
            <div className="sd-section-header" style={{ marginBottom: '1rem' }}>
              <Calendar size={18} className="text-secondary" />
              <h2>Academic Calendar — Upcoming Events</h2>
              <span className="count-badge">{upcomingEvents.length}</span>
            </div>
            {upcomingEvents.length === 0 ? (
              <div className="sd-empty" style={{ padding: '2rem 0' }}>
                <Calendar size={40} color="#5F6368" />
                <h3>No upcoming events</h3>
                <p>Events from the academic calendar will appear here.</p>
              </div>
            ) : (
              <div className="sd-events-list">
                {upcomingEvents.map((evt, i) => (
                  <div key={i} className="sd-event-row">
                    <div className="sd-event-date">
                      {new Date(evt.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
                    </div>
                    <div className="sd-event-info">
                      <div className="sd-event-title">{evt.title}</div>
                      {evt.description && <div className="sd-event-desc">{evt.description}</div>}
                    </div>
                    <div className="sd-event-tags">
                      {evt.audience && <span className="sd-alert-tag audience">{evt.audience}</span>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentDashboard;
