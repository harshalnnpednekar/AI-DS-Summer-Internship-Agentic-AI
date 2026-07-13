import React, { useState, useEffect } from 'react';
import { AlertTriangle, Download, Send, CheckSquare, Square, Loader, ChevronDown, ChevronUp } from 'lucide-react';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import './Pages.css';
import './DefaulterManagement.css';

const DefaulterManagement = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [collapsedClasses, setCollapsedClasses] = useState({});

  useEffect(() => {
    const fetchDefaulters = async () => {
      try {
        const token = localStorage.getItem('accessToken');
        const response = await fetch('/api/attendance/defaulters', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        if (data && data.success) {
          setStudents(data.data);
        }
      } catch (error) {
        console.error('Error fetching defaulters:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchDefaulters();
  }, []);

  const toggleCheck = (classKey, rollId) => {
    setStudents(prev => prev.map(s =>
      s.class === classKey && s.id === rollId ? { ...s, checked: !s.checked } : s
    ));
  };

  const toggleClass = (className) => {
    setCollapsedClasses(prev => ({ ...prev, [className]: !prev[className] }));
  };

  // Group students by class, preserving sort order
  const grouped = students.reduce((acc, s) => {
    if (!acc[s.class]) acc[s.class] = [];
    acc[s.class].push(s);
    return acc;
  }, {});

  const selectedCount = students.filter(s => s.checked).length;

  const handleBroadcast = async () => {
    const selectedIds = students.map(s => s.id);
    if (selectedIds.length === 0) {
      alert('No students to broadcast.');
      return;
    }
    
    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch('/api/attendance/defaulters/broadcast', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ defaulter_ids: selectedIds })
      });
      const data = await response.json();
      if (data && data.success) {
        alert(data.data || 'Emails successfully broadcasted to the entire class as per service.');
      } else {
        alert('Failed to broadcast.');
      }
    } catch (error) {
      console.error('Error broadcasting:', error);
      alert('Error broadcasting.');
    }
  };


  const exportToPDF = () => {
    if (students.length === 0) {
      alert('No data to export.');
      return;
    }

    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.width;
    const pageHeight = doc.internal.pageSize.height;
    
    // ==========================================
    // COVER PAGE
    // ==========================================
    doc.setFillColor(30, 41, 59); // slate-800
    doc.rect(0, 0, pageWidth, pageHeight, 'F');
    
    doc.setTextColor(255, 255, 255);
    doc.setFont('times', 'bold');
    doc.setFontSize(28);
    doc.text('OmniSync Education', pageWidth / 2, 80, { align: 'center' });
    
    doc.setFont('times', 'italic');
    doc.setFontSize(16);
    doc.setTextColor(148, 163, 184);
    doc.text('Office of the Academic Registrar', pageWidth / 2, 90, { align: 'center' });
    
    doc.setDrawColor(100, 116, 139);
    doc.setLineWidth(0.5);
    doc.line(pageWidth / 2 - 40, 100, pageWidth / 2 + 40, 100);
    
    doc.setFont('times', 'bold');
    doc.setFontSize(24);
    doc.setTextColor(255, 255, 255);
    doc.text('OFFICIAL DEFAULTER AUDIT', pageWidth / 2, 120, { align: 'center' });
    
    doc.setFont('times', 'normal');
    doc.setFontSize(12);
    doc.setTextColor(203, 213, 225);
    doc.text(`Generated on ${new Date().toLocaleDateString()} at ${new Date().toLocaleTimeString()}`, pageWidth / 2, 130, { align: 'center' });
    
    // Summary Metrics on Cover Page
    doc.setFillColor(15, 23, 42);
    doc.rect(pageWidth / 2 - 60, 160, 120, 60, 'F');
    doc.setDrawColor(71, 85, 105);
    doc.rect(pageWidth / 2 - 60, 160, 120, 60, 'D');
    
    doc.setFont('times', 'bold');
    doc.setFontSize(14);
    doc.setTextColor(255, 255, 255);
    doc.text('AUDIT SUMMARY', pageWidth / 2, 172, { align: 'center' });
    
    doc.setFontSize(12);
    doc.setFont('times', 'normal');
    doc.setTextColor(148, 163, 184);
    doc.text('Total Defaulters Identified:', pageWidth / 2 - 50, 185);
    doc.setTextColor(255, 255, 255);
    doc.text(`${students.length}`, pageWidth / 2 + 40, 185, { align: 'right' });
    
    const criticalCount = students.filter(s => s.status === 'Critical').length;
    doc.setTextColor(148, 163, 184);
    doc.text('Critical Action Required:', pageWidth / 2 - 50, 195);
    doc.setTextColor(239, 68, 68); // Red
    doc.text(`${criticalCount}`, pageWidth / 2 + 40, 195, { align: 'right' });
    
    const classes = Object.keys(grouped);
    doc.setTextColor(148, 163, 184);
    doc.text('Departments/Classes Affected:', pageWidth / 2 - 50, 205);
    doc.setTextColor(255, 255, 255);
    doc.text(`${classes.length}`, pageWidth / 2 + 40, 205, { align: 'right' });
    
    doc.addPage();
    
    // ==========================================
    // DATA PAGES
    // ==========================================
    let y = 30;
    
    classes.forEach((classKey, idx) => {
      if (y > pageHeight - 60) {
        doc.addPage();
        y = 30;
      }

      // Formal Section Header
      doc.setFont('times', 'bold');
      doc.setFontSize(16);
      doc.setTextColor(15, 23, 42);
      doc.text(`Class Roster: ${classKey}`, 14, y);
      
      const classStudents = grouped[classKey];
      doc.setFont('times', 'italic');
      doc.setFontSize(10);
      doc.setTextColor(100, 116, 139);
      doc.text(`Identified Defaulters: ${classStudents.length}`, pageWidth - 14, y, { align: 'right' });
      
      doc.setDrawColor(15, 23, 42);
      doc.setLineWidth(1);
      doc.line(14, y + 4, pageWidth - 14, y + 4);
      
      y += 10;
      
      const tableData = classStudents.map(s => [
        s.roll || s.id.split('-')[0],
        s.name,
        s.theory_attendance === 'N/A' ? '-' : `${s.theory_attendance}%`,
        s.practical_attendance === 'N/A' ? '-' : `${s.practical_attendance}%`,
        `${s.attendance}%`,
        s.status.toUpperCase()
      ]);

      autoTable(doc, {
        startY: y,
        head: [['Roll No.', 'Student Name', 'Theory', 'Practical', 'Total', 'Status']],
        body: tableData,
        theme: 'plain',
        styles: { 
          font: 'times', 
          fontSize: 10, 
          cellPadding: 6,
          textColor: [30, 41, 59],
          lineWidth: 0.1,
          lineColor: [203, 213, 225]
        },
        headStyles: { 
          fillColor: [241, 245, 249], 
          textColor: [15, 23, 42], 
          fontStyle: 'bold',
          lineWidth: { bottom: 1 },
          lineColor: [15, 23, 42]
        },
        columnStyles: { 
          0: { cellWidth: 20 }, 
          1: { cellWidth: 'auto' },
          2: { halign: 'center', cellWidth: 25 }, 
          3: { halign: 'center', cellWidth: 25 }, 
          4: { halign: 'center', cellWidth: 25, fontStyle: 'bold' }, 
          5: { halign: 'center', cellWidth: 25, fontStyle: 'bold' } 
        },
        didParseCell: function(data) {
          if (data.section === 'body' && data.column.index === 5) {
             if (data.cell.raw === 'CRITICAL') {
                data.cell.styles.textColor = [185, 28, 28]; // Dark red
             } else {
                data.cell.styles.textColor = [180, 83, 9]; // Dark amber
             }
          }
        }
      });
      
      y = doc.lastAutoTable.finalY + 20;
    });

    // ==========================================
    // OFFICIAL SIGNATURE BLOCK
    // ==========================================
    if (y > pageHeight - 60) {
      doc.addPage();
      y = 40;
    } else {
      y += 20;
    }
    
    doc.setDrawColor(15, 23, 42);
    doc.setLineWidth(0.5);
    doc.line(14, y, 70, y);
    doc.line(pageWidth - 70, y, pageWidth - 14, y);
    
    doc.setFont('times', 'bold');
    doc.setFontSize(10);
    doc.setTextColor(15, 23, 42);
    doc.text('Head of Department', 42, y + 5, { align: 'center' });
    doc.text('Academic Registrar', pageWidth - 42, y + 5, { align: 'center' });
    
    doc.setFont('times', 'normal');
    doc.setTextColor(100, 116, 139);
    doc.text('(Signature & Date)', 42, y + 10, { align: 'center' });
    doc.text('(Signature & Date)', pageWidth - 42, y + 10, { align: 'center' });

    // ==========================================
    // FOOTER (Page Numbers)
    // ==========================================
    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 2; i <= pageCount; i++) { // Skip cover page
      doc.setPage(i);
      doc.setFont('times', 'normal');
      doc.setFontSize(9);
      doc.setTextColor(148, 163, 184);
      doc.text(`OmniSync Education - Official Academic Audit | Page ${i} of ${pageCount}`, pageWidth / 2, pageHeight - 12, { align: 'center' });
    }

    doc.save('OmniSync_Defaulter_Audit_Report.pdf');
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">Automated Defaulter Management</h1>
        <p className="page-subtitle">Auto-generated from live attendance data. Awaiting HOD approval before broadcast.</p>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem', padding: '1.5rem', borderLeft: '4px solid var(--color-primary)' }}>
        <h3 style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <AlertTriangle size={20} color="var(--color-primary)" />
          Defaulter Management Workflow & Identification Criteria
        </h3>
        <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem', marginBottom: '1.25rem', lineHeight: '1.5' }}>
          This automated module strictly monitors academic compliance by aggregating live attendance metrics across all conducted sessions. The workflow enforces university protocols for identifying and managing students failing to meet minimum attendance thresholds.
        </p>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
            <div style={{ width: '28px', height: '28px', borderRadius: '50%', backgroundColor: 'rgba(16, 185, 129, 0.1)', color: 'var(--color-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 600, fontSize: '0.875rem', flexShrink: 0 }}>1</div>
            <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem', lineHeight: '1.5', marginTop: '0.2rem' }}>
              <strong style={{ color: 'var(--color-text-primary)' }}>Data Aggregation (Theory & Practical):</strong> The system calculates absolute attendance independently for Theory and Practical sessions. If a specific session type has not yet been conducted, it is excluded from the aggregate to prevent data skewing.
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
            <div style={{ width: '28px', height: '28px', borderRadius: '50%', backgroundColor: 'rgba(16, 185, 129, 0.1)', color: 'var(--color-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 600, fontSize: '0.875rem', flexShrink: 0 }}>2</div>
            <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem', lineHeight: '1.5', marginTop: '0.2rem' }}>
              <strong style={{ color: 'var(--color-text-primary)' }}>Threshold Calculation:</strong> Students dropping below the <strong style={{color: 'var(--color-warning)'}}>75%</strong> university mandate are flagged as <strong>At Risk</strong>. If attendance deteriorates below <strong style={{color: 'var(--color-danger)'}}>50%</strong>, the system escalates their status to <strong>Critical</strong>, demanding immediate academic intervention.
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
            <div style={{ width: '28px', height: '28px', borderRadius: '50%', backgroundColor: 'rgba(16, 185, 129, 0.1)', color: 'var(--color-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 600, fontSize: '0.875rem', flexShrink: 0 }}>3</div>
            <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem', lineHeight: '1.5', marginTop: '0.2rem' }}>
              <strong style={{ color: 'var(--color-text-primary)' }}>HOD Verification & Approval:</strong> All generated reports are held in a pending state for final review by the Head of Department. The HOD can export the official data matrix for offline auditing before taking disciplinary action.
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
            <div style={{ width: '28px', height: '28px', borderRadius: '50%', backgroundColor: 'rgba(16, 185, 129, 0.1)', color: 'var(--color-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 600, fontSize: '0.875rem', flexShrink: 0 }}>4</div>
            <div style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem', lineHeight: '1.5', marginTop: '0.2rem' }}>
              <strong style={{ color: 'var(--color-text-primary)' }}>Automated Broadcasting:</strong> Upon HOD approval, the system executes a mass broadcast, automatically dispatching formal warning communications directly to the registered emails of all flagged students and their guardians.
            </div>
          </div>
        </div>
      </div>

      <div className="card" style={{ padding: 0 }}>
        <div className="defaulter-action-bar">
          <div className="defaulter-info" style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertTriangle className="text-danger" size={20} />
              <span className="font-semibold" style={{ color: 'var(--color-text-primary)', fontSize: '1.125rem' }}>Defaulter List</span>
            </div>
            <span className="font-semibold" style={{ color: 'var(--color-text-primary)' }}>{students.length} students identified</span>
            <span className="font-semibold" style={{ color: 'var(--color-text-primary)' }}>Generated {new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
          </div>
          <div className="defaulter-actions" style={{ display: 'flex', gap: '1rem' }}>
            <button className="btn btn-primary" style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }} onClick={exportToPDF}>
              <Download size={16} /> Export Official PDF
            </button>
            <button className="btn btn-primary" style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }} onClick={handleBroadcast}>
              <Send size={16} /> Approve &amp; Broadcast Defaulter List
            </button>
          </div>
        </div>

        <div className="table-responsive">
          {loading ? (
            <div style={{ textAlign: 'center', padding: '3rem' }}>
              <Loader size={28} style={{ margin: '0 auto', display: 'block', color: 'var(--color-primary)' }} />
              <p style={{ marginTop: '0.75rem', color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>Calculating attendance...</p>
            </div>
          ) : students.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--color-text-secondary)' }}>
              No defaulters found — all students are above 75% attendance.
            </div>
          ) : (
            Object.entries(grouped).map(([className, classStudents]) => {
              const isCollapsed = collapsedClasses[className];
              const criticalCount = classStudents.filter(s => s.status === 'Critical').length;
              const atRiskCount = classStudents.filter(s => s.status === 'At Risk').length;

              return (
                <div key={className} className="class-group">
                  {/* Class header row */}
                  <div
                    className="class-group-header"
                    onClick={() => toggleClass(className)}
                    style={{ cursor: 'pointer' }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <span className="class-badge" style={{ fontSize: '0.8rem' }}>{className}</span>
                      <span className="font-semibold" style={{ fontSize: '0.875rem' }}>{classStudents.length} student{classStudents.length !== 1 ? 's' : ''}</span>
                      {criticalCount > 0 && (
                        <span className="status-badge-outline critical" style={{ fontSize: '0.7rem', padding: '0.1rem 0.5rem' }}>
                          {criticalCount} Critical
                        </span>
                      )}
                      {atRiskCount > 0 && (
                        <span className="status-badge-outline risk" style={{ fontSize: '0.7rem', padding: '0.1rem 0.5rem' }}>
                          {atRiskCount} At Risk
                        </span>
                      )}
                    </div>
                    {isCollapsed ? <ChevronDown size={16} /> : <ChevronUp size={16} />}
                  </div>

                  {/* Table for this class */}
                  {!isCollapsed && (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th style={{ textAlign: 'center' }}>ROLL NO.</th>
                          <th style={{ textAlign: 'center' }}>STUDENT NAME</th>
                          <th style={{ textAlign: 'center' }}>THEORY ATTENDANCE %</th>
                          <th style={{ textAlign: 'center' }}>PRACTICAL ATTENDANCE %</th>
                          <th style={{ textAlign: 'center' }}>TOTAL ATTENDANCE %</th>
                          <th style={{ textAlign: 'center' }}>STATUS</th>
                        </tr>
                      </thead>
                      <tbody>
                        {classStudents.map((s, idx) => (
                          <tr key={idx}>
                            <td className="font-medium" style={{ textAlign: 'center' }}>
                              {s.roll || s.id.split('-')[0]}
                            </td>
                            <td style={{ textAlign: 'center', color: 'var(--color-text-secondary)', fontSize: '0.825rem' }}>
                              {(s.name && s.name !== s.id) ? s.name : (s.roll || s.id.split('-')[0])}
                            </td>
                            <td style={{ textAlign: 'center' }}>
                              <div className="progress-cell" style={{ justifyContent: 'center' }}>
                                <div className="progress-bar-bg" style={{ width: '60px' }}>
                                  <div
                                    className={`progress-bar-fill ${s.theory_attendance === 'N/A' ? 'bg-secondary' : s.theory_attendance < 50 ? 'bg-danger' : 'bg-warning'}`}
                                    style={{ width: `${s.theory_attendance === 'N/A' ? 0 : s.theory_attendance}%` }}
                                  ></div>
                                </div>
                                <span className="font-semibold" style={{ fontSize: '0.875rem', minWidth: '38px' }}>
                                  {s.theory_attendance === 'N/A' ? 'N/A' : `${s.theory_attendance}%`}
                                </span>
                              </div>
                            </td>
                            <td style={{ textAlign: 'center' }}>
                              <div className="progress-cell" style={{ justifyContent: 'center' }}>
                                <div className="progress-bar-bg" style={{ width: '60px' }}>
                                  <div
                                    className={`progress-bar-fill ${s.practical_attendance === 'N/A' ? 'bg-secondary' : s.practical_attendance < 50 ? 'bg-danger' : 'bg-warning'}`}
                                    style={{ width: `${s.practical_attendance === 'N/A' ? 0 : s.practical_attendance}%` }}
                                  ></div>
                                </div>
                                <span className="font-semibold" style={{ fontSize: '0.875rem', minWidth: '38px' }}>
                                  {s.practical_attendance === 'N/A' ? 'N/A' : `${s.practical_attendance}%`}
                                </span>
                              </div>
                            </td>
                            <td style={{ textAlign: 'center' }}>
                              <div className="progress-cell" style={{ justifyContent: 'center' }}>
                                <div className="progress-bar-bg" style={{ width: '80px' }}>
                                  <div
                                    className={`progress-bar-fill ${s.attendance < 50 ? 'bg-danger' : 'bg-warning'}`}
                                    style={{ width: `${s.attendance}%` }}
                                  ></div>
                                </div>
                                <span className="font-semibold" style={{ fontSize: '0.875rem', minWidth: '38px' }}>{s.attendance}%</span>
                              </div>
                            </td>
                            <td style={{ textAlign: 'center' }}>
                              <span className={`status-badge-outline ${s.status === 'Critical' ? 'critical' : 'risk'}`}>
                                {s.status}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              );
            })
          )}
        </div>

        <div className="table-footer" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span className="font-medium text-sm">{selectedCount} of {students.length} selected</span>
          <span className="text-success text-sm flex-center" style={{ gap: '0.25rem' }}>
            <CheckCircle2Icon /> Pending HOD approval before broadcast
          </span>
        </div>
      </div>
    </div>
  );
};

const CheckCircle2Icon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
    <polyline points="22 4 12 14.01 9 11.01"></polyline>
  </svg>
);

export default DefaulterManagement;
