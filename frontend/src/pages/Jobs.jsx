import { useState, useEffect } from 'react';
import api from '../services/api';
import { Briefcase, MapPin, DollarSign, ExternalLink, Clock, Target, Mail, Trash2 } from 'lucide-react';

export default function Jobs() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const { data } = await api.get('/jobs');
        setJobs(data);
      } catch (err) {
        console.error(err);
        setError("Failed to load jobs. Make sure the backend is running.");
      } finally {
        setLoading(false);
      }
    };
    fetchJobs();
  }, []);

  const handleSendEmail = async () => {
    try {
      await api.post('/reports/email');
      alert("Email dispatched successfully!");
    } catch (err) {
      alert("Failed to send email. Check backend logs.");
    }
  };

  const handleDeleteJob = async (jobId) => {
    try {
      await api.delete(`/jobs/${jobId}/match`);
      setJobs(jobs.filter(job => job.id !== jobId));
    } catch (err) {
      console.error(err);
      alert("Failed to delete job match.");
    }
  };

  if (loading) return <div style={{ padding: '40px', fontSize: '18px' }}>Fetching latest jobs...</div>;
  if (error) return <div style={{ padding: '40px', color: 'red' }}>{error}</div>;

  return (
    <div className="animate-fade-in" style={styles.container}>
      <div style={styles.header}>
        <div>
          <h1 style={{ fontSize: '32px', margin: 0, marginBottom: '8px' }}>Matched Jobs</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '16px', margin: 0 }}>
            Based on your latest intelligence reports and preferences.
          </p>
        </div>
        <button onClick={handleSendEmail} style={styles.emailButton}>
          <Mail size={18} /> Send to Email
        </button>
      </div>

      {jobs.length === 0 ? (
        <div className="glass-panel" style={{ padding: '40px', textAlign: 'center' }}>
          <Briefcase size={48} color="var(--text-secondary)" style={{ marginBottom: '16px', opacity: 0.5 }} />
          <h3 style={{ fontSize: '20px', marginBottom: '8px' }}>No jobs found yet</h3>
          <p style={{ color: 'var(--text-secondary)' }}>Run a scan on the dashboard to populate jobs.</p>
        </div>
      ) : (
        <div style={styles.grid}>
          {jobs.map(job => (
            <div key={job.id} className="glass-panel hover-scale" style={styles.card}>
              <div style={styles.cardHeader}>
                <div>
                  <h3 style={styles.jobTitle}>{job.title}</h3>
                  <div style={styles.companyName}>
                    {job.company}
                  </div>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', alignItems: 'flex-end' }}>
                  {job.final_score && (
                    <div style={styles.scoreBadge}>
                      <Target size={14} /> {Math.round(job.final_score)}% Match
                    </div>
                  )}
                  <button 
                    onClick={() => handleDeleteJob(job.id)}
                    style={styles.deleteButton}
                    title="Remove from matches"
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

              {job.skills && job.skills.length > 0 && (
                <div style={styles.skills}>
                  {job.skills.slice(0, 4).map(skill => (
                    <span key={skill} style={styles.skillTag}>{skill}</span>
                  ))}
                  {job.skills.length > 4 && (
                    <span style={styles.skillTag}>+{job.skills.length - 4} more</span>
                  )}
                </div>
              )}

              <div style={styles.cardFooter}>
                <a 
                  href={job.apply_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  style={styles.applyButton}
                >
                  Apply Now <ExternalLink size={16} />
                </a>
              </div>
            </div>
          ))}
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
    marginBottom: '32px',
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
    transition: 'opacity 0.2s ease',
    boxShadow: 'var(--shadow-sm)'
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
    position: 'relative',
    transition: 'transform 0.2s ease, box-shadow 0.2s ease',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '16px',
    gap: '12px'
  },
  jobTitle: {
    fontSize: '20px',
    fontWeight: 700,
    margin: '0 0 8px 0',
    color: 'var(--text-primary)',
    lineHeight: 1.2
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
    boxShadow: 'var(--shadow-sm)'
  },
  metaInfo: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
    marginBottom: '20px',
  },
  metaItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '14px',
    color: 'var(--text-secondary)',
  },
  skills: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '8px',
    marginTop: 'auto',
    marginBottom: '20px'
  },
  skillTag: {
    background: 'rgba(255,255,255,0.4)',
    border: '1px solid rgba(255,255,255,0.6)',
    padding: '4px 10px',
    borderRadius: '16px',
    fontSize: '12px',
    color: 'var(--text-primary)',
    fontWeight: 500
  },
  cardFooter: {
    marginTop: 'auto',
    borderTop: '1px solid rgba(0,0,0,0.05)',
    paddingTop: '16px',
    display: 'flex',
    justifyContent: 'flex-end'
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
    transition: 'opacity 0.2s ease',
    boxShadow: 'var(--shadow-md)'
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
    transition: 'all 0.2s ease'
  }
};
