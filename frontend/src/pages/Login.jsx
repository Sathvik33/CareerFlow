import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import { LogIn } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login, user } = useAuth();

  useEffect(() => {
    if (user) {
      navigate('/dashboard');
    }
  }, [user, navigate]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const { data } = await api.post('/users/login', { email, password });
      await login(data.token, data.refresh_token);
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div className="glass-panel animate-fade-in" style={styles.card}>
        <div style={styles.header}>
          <h1 className="text-gradient" style={styles.title}>CareerFlow AI</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Welcome back to your intelligence hub.</p>
        </div>

        {error && <div style={styles.error}>{error}</div>}

        <form onSubmit={handleLogin} style={styles.form}>
          <div style={styles.inputGroup}>
            <label style={styles.label}>Email</label>
            <input 
              type="email" 
              value={email} 
              onChange={(e) => setEmail(e.target.value)} 
              style={styles.input} 
              required 
            />
          </div>
          <div style={styles.inputGroup}>
            <label style={styles.label}>Password</label>
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              style={styles.input} 
              required 
            />
          </div>
          
          <button type="submit" disabled={loading} style={styles.button}>
            <LogIn size={20} />
            {loading ? 'Authenticating...' : 'Login'}
          </button>
        </form>

        <p style={styles.footer}>
          Don't have an account? <Link to="/signup" style={{ fontWeight: 600 }}>Sign up</Link>
        </p>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '20px',
    // Soft radial background to compliment the beige
    background: 'radial-gradient(circle at center, #FDFBF7 0%, #EAE6DF 100%)'
  },
  card: {
    width: '100%',
    maxWidth: '400px',
    padding: '40px',
    display: 'flex',
    flexDirection: 'column',
    gap: '24px'
  },
  header: {
    textAlign: 'center',
    marginBottom: '8px'
  },
  title: {
    fontSize: '32px',
    marginBottom: '8px'
  },
  error: {
    backgroundColor: '#FFEAEA',
    color: '#D8000C',
    padding: '12px',
    borderRadius: '8px',
    fontSize: '14px',
    textAlign: 'center'
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px'
  },
  inputGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px'
  },
  label: {
    fontSize: '14px',
    fontWeight: 500,
    color: 'var(--text-primary)'
  },
  input: {
    padding: '12px 16px',
    borderRadius: 'var(--radius-sm)',
    border: '1px solid var(--border-color)',
    backgroundColor: 'rgba(255, 255, 255, 0.8)',
    fontSize: '16px',
    outline: 'none',
    transition: 'border var(--transition-fast)'
  },
  button: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    padding: '14px',
    marginTop: '8px',
    backgroundColor: 'var(--primary)',
    color: '#FFF',
    border: 'none',
    borderRadius: 'var(--radius-sm)',
    fontSize: '16px',
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'background var(--transition-fast), transform var(--transition-fast)'
  },
  footer: {
    textAlign: 'center',
    fontSize: '14px',
    color: 'var(--text-secondary)'
  }
};
