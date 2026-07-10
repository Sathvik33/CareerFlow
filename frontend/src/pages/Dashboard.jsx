import { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Briefcase, TrendingUp, Building, Zap, AlertTriangle, Lightbulb, X, FileText, Settings } from 'lucide-react';

export default function Dashboard() {
  const { user } = useAuth();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [greeting, setGreeting] = useState('');
  const [scanning, setScanning] = useState(false);
  const [scanMessage, setScanMessage] = useState('');
  const [scanLogs, setScanLogs] = useState([]);
  
  const JOB_BOARDS = [
    'boards.greenhouse.io', 'jobs.lever.co', 'remoteok.com', 'remotive.com', 
    'usajobs.gov'
  ];
  const [targetWebsites, setTargetWebsites] = useState(['boards.greenhouse.io', 'jobs.lever.co', 'remoteok.com']);
  const [maxJobs, setMaxJobs] = useState(5);

  const toggleWebsite = (site) => {
    setTargetWebsites(prev => 
      prev.includes(site) ? prev.filter(s => s !== site) : [...prev, site]
    );
  };

  const fetchReport = async () => {
    try {
      const { data } = await api.get('/reports/latest');
      setReport(data.report_json);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, []);

  const handleScanJobs = async () => {
    setScanning(true);
    setScanMessage('');
    setScanLogs([]);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/reports/stream-scan', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          websites: targetWebsites,
          max_jobs: maxJobs
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        setScanMessage(errorData.detail || 'Failed to start scan. Ensure you have a Resume & Preferences.');
        setScanning(false);
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');
        
        for (let line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.substring(6);
            if (!dataStr) continue;
            try {
              const data = JSON.parse(dataStr);
              if (data.message) {
                setScanLogs(prev => [...prev, data.message]);
              }
              if (data.error) {
                setScanMessage(data.error);
                setScanning(false);
              }
              if (data.done) {
                setScanning(false);
                setScanMessage('Scan complete! Your new report is ready.');
                fetchReport();
              }
            } catch (e) {
              console.error("Error parsing stream JSON", e);
            }
          }
        }
      }
    } catch (err) {
      setScanMessage('Connection to streaming server failed.');
      setScanning(false);
    }
  };

  useEffect(() => {
    const greetings = [
      "Welcome back",
      "Ready to crush it today",
      "Here is your latest intelligence",
      "Let's find your dream job"
    ];
    const random = greetings[Math.floor(Math.random() * greetings.length)];
    setGreeting(`${random}, ${user?.name?.split(' ')[0] || 'User'}!`);

    const hasSeenOnboarding = localStorage.getItem('hasSeenOnboarding');
    if (!hasSeenOnboarding && user) {
      setShowOnboarding(true);
    }
  }, [user]);

  const closeOnboarding = () => {
    localStorage.setItem('hasSeenOnboarding', 'true');
    setShowOnboarding(false);
  };



  if (loading) return <div style={{padding: '40px'}}>Loading your intelligence...</div>;

  return (
    <div className="animate-fade-in" style={styles.container}>
      
      {/* Onboarding Modal */}
      {showOnboarding && (
        <div style={styles.modalOverlay}>
          <div className="glass-panel" style={styles.modalContent}>
            <button onClick={closeOnboarding} style={styles.closeButton}><X size={24} /></button>
            <h2 style={{fontSize: '28px', marginBottom: '16px', color: 'var(--text-primary)'}}>Welcome to CareerFlow! 🚀</h2>
            <p style={{fontSize: '16px', color: 'var(--text-secondary)', marginBottom: '24px'}}>
              This AI application actively scrapes jobs, parses your skills, and builds a personalized daily intelligence report for you.
            </p>
            <div style={{display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '32px'}}>
              <div style={styles.stepBox}>
                <Settings color="var(--primary)" size={24} />
                <div>
                  <strong>Step 1: Set Preferences</strong>
                  <p style={{fontSize: '14px', color: 'var(--text-secondary)'}}>Go to Preferences and tell us your target roles and salary.</p>
                </div>
              </div>
              <div style={styles.stepBox}>
                <FileText color="var(--primary)" size={24} />
                <div>
                  <strong>Step 2: Upload Resume</strong>
                  <p style={{fontSize: '14px', color: 'var(--text-secondary)'}}>Head to the Resume Hub and drop your PDF to get AI embedded.</p>
                </div>
              </div>
              <div style={styles.stepBox}>
                <Zap color="var(--primary)" size={24} />
                <div>
                  <strong>Step 3: Get Daily Reports</strong>
                  <p style={{fontSize: '14px', color: 'var(--text-secondary)'}}>Check this Dashboard daily for high-match jobs and insights.</p>
                </div>
              </div>
            </div>
            <button onClick={closeOnboarding} style={styles.primaryButton}>Let's Get Started</button>
          </div>
        </div>
      )}

      <h1 style={{ fontSize: '32px', margin: 0, marginBottom: '8px' }}>{greeting}</h1>
      <p style={styles.subtitle}>Your personalized AI career analysis.</p>

      <div className="glass-panel" style={{ ...styles.card, marginBottom: '24px' }}>
        <h3 style={{ fontSize: '18px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Settings size={20} color="var(--primary)" />
          Scan Configuration
        </h3>
        
        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '12px', color: 'var(--text-secondary)' }}>Target Job Boards</label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
            {JOB_BOARDS.map(site => (
              <label key={site} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '14px', cursor: 'pointer', textTransform: 'capitalize' }}>
                <input 
                  type="checkbox" 
                  checked={targetWebsites.includes(site)} 
                  onChange={() => toggleWebsite(site)} 
                  disabled={scanning}
                  style={{ accentColor: 'var(--primary)', width: '16px', height: '16px' }}
                />
                {site.replace('.com', '')}
              </label>
            ))}
          </div>
        </div>

        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, marginBottom: '8px', color: 'var(--text-secondary)' }}>Total Jobs to Fetch & Match</label>
          <input 
            type="number" 
            value={maxJobs} 
            onChange={(e) => setMaxJobs(parseInt(e.target.value) || 5)}
            disabled={scanning}
            min={1}
            max={50}
            style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid var(--border-color)', outline: 'none', width: '150px', fontSize: '15px' }}
          />
        </div>

        <button 
          onClick={handleScanJobs} 
          disabled={scanning || targetWebsites.length === 0} 
          style={{...styles.primaryButton, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '14px 24px', width: 'auto'}}
        >
          <Zap size={18} />
          {scanning ? 'Initializing AI Agents...' : 'Start Job Search'}
        </button>
      </div>

      {scanMessage && (
        <div style={{
          padding: '16px', 
          backgroundColor: scanMessage.includes('Failed') ? '#FFEAEA' : '#E8F6EF', 
          color: scanMessage.includes('Failed') ? '#D8000C' : '#27AE60', 
          borderRadius: 'var(--radius-sm)', 
          marginBottom: '24px', 
          fontWeight: 500
        }}>
          {scanMessage}
        </div>
      )}

      {scanning && (
        <div style={{
          backgroundColor: '#1E293B',
          borderRadius: '8px',
          padding: '16px',
          fontFamily: 'monospace',
          color: '#2ECC71',
          marginBottom: '24px',
          maxHeight: '300px',
          overflowY: 'auto',
          boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.5)',
          fontSize: '14px',
          lineHeight: 1.5
        }}>
          <div style={{ marginBottom: '12px', color: '#94A3B8', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '1px' }}>-- Live Agent Execution Terminal --</div>
          {scanLogs.map((log, i) => (
            <div key={i} style={{ marginBottom: '6px' }}>
              <span style={{color: '#94A3B8'}}>{'>'}</span> {log}
            </div>
          ))}
          <div className="animate-pulse" style={{ marginTop: '6px' }}><span style={{color: '#94A3B8'}}>{'>'}</span> _</div>
        </div>
      )}

      {!report ? (
        <div className="glass-panel" style={{ ...styles.card, textAlign: 'center', padding: '60px 20px', marginTop: '32px' }}>
          <Zap size={48} color="var(--primary)" style={{ marginBottom: '16px' }} />
          <h2>AI Agents are analyzing your profile.</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>
            Upload your resume and set your preferences. Your first daily report will appear here soon once the background agents complete their tasks.
          </p>
        </div>
      ) : (
        <>
          <div style={styles.metricsGrid}>
            <div className="glass-panel" style={styles.metricCard}>
              <div style={styles.metricHeader}>
                <Briefcase size={24} color="var(--primary)" />
                <span style={styles.metricLabel}>New Jobs Found</span>
              </div>
              <span style={styles.metricValue}>{report.new_jobs}</span>
            </div>
            
            <div className="glass-panel" style={styles.metricCard}>
              <div style={styles.metricHeader}>
                <TrendingUp size={24} color="#2ECC71" />
                <span style={styles.metricLabel}>High Match Potential</span>
              </div>
              <span style={styles.metricValue}>{report.high_match_jobs}</span>
            </div>
            
            <div className="glass-panel" style={styles.metricCard}>
              <div style={styles.metricHeader}>
                <Building size={24} color="var(--secondary)" />
                <span style={styles.metricLabel}>Top Companies</span>
              </div>
              <span style={styles.metricValueText}>{report.top_companies?.join(', ') || 'N/A'}</span>
            </div>
          </div>

          <div style={styles.contentGrid}>
            <div className="glass-panel" style={styles.card}>
              <h3 style={styles.cardTitle}><Zap size={20} color="#F1C40F"/> Profile Strengths</h3>
              <ul style={styles.list}>
                {report.strengths?.map((s, i) => <li key={i} style={styles.listItem}>{s}</li>)}
              </ul>
            </div>
            
            <div className="glass-panel" style={styles.card}>
              <h3 style={styles.cardTitle}><AlertTriangle size={20} color="#E74C3C"/> Skill Gaps Identified</h3>
              <ul style={styles.list}>
                {report.weaknesses?.map((w, i) => <li key={i} style={styles.listItem}>{w}</li>)}
              </ul>
            </div>
          </div>

          <div className="glass-panel" style={{...styles.card, marginTop: '24px'}}>
            <h3 style={styles.cardTitle}><Building size={20} color="var(--primary)"/> Live Company Insights</h3>
            <div style={styles.insights}>
              {report.company_insights && Object.entries(report.company_insights).map(([company, insight], i) => (
                <div key={i} style={styles.insightItem}>
                  <strong style={{ fontSize: '16px' }}>{company}</strong>
                  <p style={{ marginTop: '6px', fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{insight}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="glass-panel" style={{...styles.card, marginTop: '24px', background: 'var(--gradient-positive)', color: 'var(--text-primary)'}}>
            <h3 style={{...styles.cardTitle, color: 'var(--text-primary)'}}><Lightbulb size={20}/> AI Recommended Action</h3>
            <p style={{ fontSize: '16px', fontWeight: 600, marginTop: '8px' }}>{report.recommended_action}</p>
          </div>
        </>
      )}
    </div>
  );
}

const styles = {
  container: { maxWidth: '1000px', paddingBottom: '40px' },
  title: { fontSize: '32px', marginBottom: '8px' },
  subtitle: { color: 'var(--text-secondary)', marginBottom: '32px' },
  metricsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '24px', marginBottom: '24px' },
  metricCard: { padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' },
  metricHeader: { display: 'flex', alignItems: 'center', gap: '12px' },
  metricLabel: { fontSize: '15px', fontWeight: 600, color: 'var(--text-secondary)' },
  metricValue: { fontSize: '48px', fontWeight: 700, lineHeight: 1, color: 'var(--text-primary)' },
  metricValueText: { fontSize: '18px', fontWeight: 600, color: 'var(--text-primary)' },
  contentGrid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' },
  card: { padding: '24px' },
  cardTitle: { display: 'flex', alignItems: 'center', gap: '8px', fontSize: '18px', marginBottom: '16px' },
  list: { listStylePosition: 'inside', color: 'var(--text-secondary)', paddingLeft: '8px' },
  listItem: { marginBottom: '12px', fontSize: '15px' },
  insights: { display: 'flex', flexDirection: 'column', gap: '16px' },
  insightItem: { padding: '16px', backgroundColor: 'rgba(255,255,255,0.6)', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(255,255,255,0.8)' },
  modalOverlay: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(30, 41, 59, 0.4)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 },
  modalContent: { position: 'relative', width: '90%', maxWidth: '600px', padding: '40px', backgroundColor: 'var(--surface-color)', borderRadius: '16px' },
  closeButton: { position: 'absolute', top: '20px', right: '20px', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)' },
  stepBox: { display: 'flex', alignItems: 'center', gap: '16px', padding: '16px', backgroundColor: 'rgba(30, 41, 59, 0.03)', borderRadius: '8px' },
  primaryButton: { width: '100%', padding: '16px', backgroundColor: 'var(--primary)', color: '#FFF', border: 'none', borderRadius: '8px', fontSize: '16px', fontWeight: 600, cursor: 'pointer', transition: 'background var(--transition-fast)' }
};
