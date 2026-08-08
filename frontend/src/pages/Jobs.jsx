import { useState, useEffect, useMemo } from 'react';
import api from '../services/api';
import {
  Briefcase, MapPin, DollarSign, ExternalLink, Clock, Target, Mail, Trash2,
  ChevronDown, ChevronUp, CheckCircle2
} from 'lucide-react';

const STATUSES = [
  { key: 'all', label: 'All' },
  { key: 'matched', label: 'Matched' },
  { key: 'saved', label: 'Saved' },
  { key: 'applied', label: 'Applied' },
  { key: 'interview', label: 'Interview' },
  { key: 'offer', label: 'Offer' },
  { key: 'rejected', label: 'Rejected' },
];

const STATUS_OPTIONS = ['matched', 'saved', 'applied', 'interview', 'offer', 'rejected'];

export default function Jobs() {
  const [jobs, setJobs] = useState([]);
  const [summary, setSummary] = useState({});
  const [filter, setFilter] = useState('all');
  const [expanded, setExpanded] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = async () => {
    try {
      const params = filter === 'all' ? {} : { status: filter };
      const [{ data }, { data: counts }] = await Promise.all([
        api.get('/jobs', { params }),
        api.get('/jobs/pipeline/summary'),
      ]);
      setJobs(data);
      setSummary(counts || {});
    } catch (err) {
      console.error(err);
      setError('Failed to load jobs. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setLoading(true);
    load();
  }, [filter]);

  const totalActive = useMemo(
    () => Object.values(summary).reduce((a, b) => a + (b || 0), 0),
    [summary]
  );

  const handleSendEmail = async () => {
    try {
      await api.post('/reports/email');
      alert('Email dispatched successfully!');
    } catch {
      alert('Failed to send email. Check backend logs.');
    }
  };

  const handleStatusChange = async (jobId, status) => {
    try {
      const { data } = await api.patch(`/jobs/${jobId}/match`, { status });
      if (filter !== 'all' && data.status !== filter) {
        setJobs((prev) => prev.filter((j) => j.id !== jobId));
      } else {
        setJobs((prev) => prev.map((j) => (j.id === jobId ? { ...j, ...data } : j)));
      }
      const { data: counts } = await api.get('/jobs/pipeline/summary');
      setSummary(counts || {});
    } catch (err) {
      console.error(err);
      alert('Failed to update status.');
    }
  };

  const handleDismiss = async (jobId) => {
    try {
      await api.delete(`/jobs/${jobId}/match`);
      setJobs((prev) => prev.filter((j) => j.id !== jobId));
      const { data: counts } = await api.get('/jobs/pipeline/summary');
      setSummary(counts || {});
    } catch (err) {
      console.error(err);
      alert('Failed to dismiss job.');
    }
  };

  const handleApplyClick = async (job) => {
    if (job.status === 'matched' || job.status === 'saved') {
      await handleStatusChange(job.id, 'applied');
    }
  };

  const toggleExplain = (jobId) => {
    setExpanded((prev) => ({ ...prev, [jobId]: !prev[jobId] }));
  };

  if (loading) return <div style={{ padding: '40px', fontSize: '18px' }}>Fetching latest jobs...</div>;
  if (error) return <div style={{ padding: '40px', color: 'red' }}>{error}</div>;

  return (
    <div className="animate-fade-in" style={styles.container}>
      <div style={styles.header}>
        <div>
          <h1 style={{ fontSize: '32px', margin: 0, marginBottom: '8px' }}>Job Tracker</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '16px', margin: 0 }}>
            Match scores, skill fit, and application pipeline in one place.
          </p>
        </div>
        <button onClick={handleSendEmail} style={styles.emailButton}>
          <Mail size={18} /> Send to Email
        </button>
      </div>

      <div style={styles.pipelineBar}>
        {STATUSES.map((s) => {
          const count = s.key === 'all' ? totalActive : (summary[s.key] || 0);
          const active = filter === s.key;
          return (
            <button
              key={s.key}
              onClick={() => setFilter(s.key)}
              style={{
                ...styles.pipeTab,
                ...(active ? styles.pipeTabActive : {}),
              }}
            >
              <span>{s.label}</span>
              <span style={styles.pipeCount}>{count}</span>
            </button>
          );
        })}
      </div>

      {jobs.length === 0 ? (
        <div className="glass-panel" style={{ padding: '40px', textAlign: 'center' }}>
          <Briefcase size={48} color="var(--text-secondary)" style={{ marginBottom: '16px', opacity: 0.5 }} />
          <h3 style={{ fontSize: '20px', marginBottom: '8px' }}>No jobs in this stage</h3>
          <p style={{ color: 'var(--text-secondary)' }}>
            Run a scan on the dashboard, or pick another pipeline filter.
          </p>
        </div>
      ) : (
        <div style={styles.grid}>
          {jobs.map((job) => {
            const open = !!expanded[job.id];
            return (
              <div key={job.id} className="glass-panel hover-scale" style={styles.card}>
                <div style={styles.cardHeader}>
                  <div>
                    <h3 style={styles.jobTitle}>{job.title}</h3>
                    <div style={styles.companyName}>{job.company}</div>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', alignItems: 'flex-end' }}>
                    {job.final_score != null && (
                      <div style={styles.scoreBadge}>
                        <Target size={14} /> {Math.round(job.final_score)}% Match
                      </div>
                    )}
                    <button
                      onClick={() => handleDismiss(job.id)}
                      style={styles.deleteButton}
                      title="Dismiss"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>

                <div style={styles.metaInfo}>
                  <div style={styles.metaItem}>
                    <MapPin size={16} /> {job.location || 'Remote'}
                  </div>
                  {job.salary && (
                    <div style={styles.metaItem}>
                      <DollarSign size={16} /> {job.salary}
                    </div>
                  )}
                  <div style={styles.metaItem}>
                    <Briefcase size={16} /> {job.source}
                  </div>
                  {job.posted_date && (
                    <div style={styles.metaItem}>
                      <Clock size={16} /> {new Date(job.posted_date).toLocaleDateString()}
                    </div>
                  )}
                </div>

                <div style={styles.statusRow}>
                  <label style={styles.statusLabel}>Status</label>
                  <select
                    value={job.status || 'matched'}
                    onChange={(e) => handleStatusChange(job.id, e.target.value)}
                    style={styles.statusSelect}
                  >
                    {STATUS_OPTIONS.map((s) => (
                      <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
                    ))}
                  </select>
                </div>

                {job.skills && job.skills.length > 0 && (
                  <div style={styles.skills}>
                    {job.skills.slice(0, 4).map((skill) => (
                      <span key={skill} style={styles.skillTag}>{skill}</span>
                    ))}
                    {job.skills.length > 4 && (
                      <span style={styles.skillTag}>+{job.skills.length - 4} more</span>
                    )}
                  </div>
                )}

                <button onClick={() => toggleExplain(job.id)} style={styles.explainToggle}>
                  {open ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                  Why this match
                </button>

                {open && (
                  <div style={styles.explainPanel}>
                    <div style={styles.scoreBreakdown}>
                      <div style={styles.scoreCell}>
                        <span style={styles.scoreCellLabel}>Semantic</span>
                        <strong>{Math.round(job.semantic_score ?? 0)}%</strong>
                      </div>
                      <div style={styles.scoreCell}>
                        <span style={styles.scoreCellLabel}>Keyword (BM25)</span>
                        <strong>{Math.round(job.bm25_score ?? 0)}%</strong>
                      </div>
                      <div style={styles.scoreCell}>
                        <span style={styles.scoreCellLabel}>Final</span>
                        <strong>{Math.round(job.final_score ?? 0)}%</strong>
                      </div>
                    </div>

                    {job.strengths?.length > 0 && (
                      <div style={styles.explainBlock}>
                        <div style={styles.explainTitle}>Strengths</div>
                        <ul style={styles.explainList}>
                          {job.strengths.slice(0, 5).map((s, i) => (
                            <li key={i}>{s}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {job.missing_skills?.length > 0 && (
                      <div style={styles.explainBlock}>
                        <div style={styles.explainTitle}>Skill gaps</div>
                        <div style={styles.skills}>
                          {job.missing_skills.slice(0, 8).map((s) => (
                            <span key={s} style={styles.gapTag}>{s}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    {job.action_items?.length > 0 && (
                      <div style={styles.explainBlock}>
                        <div style={styles.explainTitle}>
                          <CheckCircle2 size={14} style={{ marginRight: 4 }} />
                          Suggested actions
                          {job.projected_improvement_pct != null && (
                            <span style={styles.improveHint}>
                              +{Math.round(job.projected_improvement_pct)}% potential
                            </span>
                          )}
                        </div>
                        <ul style={styles.explainList}>
                          {job.action_items.slice(0, 4).map((a, i) => (
                            <li key={i}>{a}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                <div style={styles.cardFooter}>
                  <a
                    href={job.apply_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={styles.applyButton}
                    onClick={() => handleApplyClick(job)}
                  >
                    Apply Now <ExternalLink size={16} />
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '20px 0',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px',
  },
  emailButton: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    background: 'var(--text-primary)',
    color: '#FFF',
    padding: '10px 20px',
    borderRadius: 'var(--radius-sm)',
    fontSize: '14px',
    fontWeight: 600,
    border: 'none',
    cursor: 'pointer',
  },
  pipelineBar: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '8px',
    marginBottom: '28px',
  },
  pipeTab: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 14px',
    borderRadius: '20px',
    border: '1px solid rgba(0,0,0,0.08)',
    background: 'rgba(255,255,255,0.5)',
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: 500,
    color: 'var(--text-secondary)',
  },
  pipeTabActive: {
    background: 'var(--primary)',
    color: '#fff',
    borderColor: 'transparent',
  },
  pipeCount: {
    fontSize: '12px',
    fontWeight: 700,
    opacity: 0.85,
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
    gap: '24px',
  },
  card: {
    padding: '24px',
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '16px',
    gap: '12px',
  },
  jobTitle: {
    fontSize: '20px',
    fontWeight: 700,
    margin: '0 0 8px 0',
    color: 'var(--text-primary)',
    lineHeight: 1.2,
  },
  companyName: {
    fontSize: '15px',
    fontWeight: 500,
    color: 'var(--text-secondary)',
  },
  scoreBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    background: 'var(--gradient-positive)',
    color: 'var(--text-primary)',
    padding: '4px 10px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: 600,
  },
  metaInfo: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
    marginBottom: '14px',
  },
  metaItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '14px',
    color: 'var(--text-secondary)',
  },
  statusRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginBottom: '14px',
  },
  statusLabel: {
    fontSize: '12px',
    fontWeight: 600,
    color: 'var(--text-secondary)',
  },
  statusSelect: {
    flex: 1,
    padding: '8px 10px',
    borderRadius: '8px',
    border: '1px solid rgba(0,0,0,0.1)',
    background: 'rgba(255,255,255,0.7)',
    fontSize: '13px',
    fontWeight: 500,
  },
  skills: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '8px',
    marginBottom: '12px',
  },
  skillTag: {
    background: 'rgba(255,255,255,0.4)',
    border: '1px solid rgba(255,255,255,0.6)',
    padding: '4px 10px',
    borderRadius: '16px',
    fontSize: '12px',
    color: 'var(--text-primary)',
    fontWeight: 500,
  },
  gapTag: {
    background: 'rgba(231, 76, 60, 0.1)',
    border: '1px solid rgba(231, 76, 60, 0.25)',
    padding: '4px 10px',
    borderRadius: '16px',
    fontSize: '12px',
    color: '#C0392B',
    fontWeight: 500,
  },
  explainToggle: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    background: 'transparent',
    border: 'none',
    color: 'var(--primary)',
    fontWeight: 600,
    fontSize: '13px',
    cursor: 'pointer',
    padding: '4px 0 12px',
    alignSelf: 'flex-start',
  },
  explainPanel: {
    background: 'rgba(0,0,0,0.03)',
    borderRadius: '12px',
    padding: '14px',
    marginBottom: '16px',
  },
  scoreBreakdown: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '8px',
    marginBottom: '12px',
  },
  scoreCell: {
    background: 'rgba(255,255,255,0.6)',
    borderRadius: '8px',
    padding: '10px 8px',
    textAlign: 'center',
  },
  scoreCellLabel: {
    display: 'block',
    fontSize: '11px',
    color: 'var(--text-secondary)',
    marginBottom: '4px',
  },
  explainBlock: {
    marginTop: '10px',
  },
  explainTitle: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontSize: '12px',
    fontWeight: 700,
    color: 'var(--text-primary)',
    marginBottom: '6px',
    textTransform: 'uppercase',
    letterSpacing: '0.03em',
  },
  explainList: {
    margin: 0,
    paddingLeft: '18px',
    fontSize: '13px',
    color: 'var(--text-secondary)',
    lineHeight: 1.45,
  },
  improveHint: {
    marginLeft: 'auto',
    fontSize: '11px',
    fontWeight: 600,
    color: 'var(--primary)',
    textTransform: 'none',
    letterSpacing: 0,
  },
  cardFooter: {
    marginTop: 'auto',
    borderTop: '1px solid rgba(0,0,0,0.05)',
    paddingTop: '16px',
    display: 'flex',
    justifyContent: 'flex-end',
  },
  applyButton: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    background: 'var(--primary)',
    color: 'white',
    padding: '10px 20px',
    borderRadius: 'var(--radius-sm)',
    fontSize: '14px',
    fontWeight: 600,
    textDecoration: 'none',
  },
  deleteButton: {
    background: 'rgba(231, 76, 60, 0.1)',
    color: '#E74C3C',
    border: 'none',
    padding: '6px',
    borderRadius: '50%',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
};
