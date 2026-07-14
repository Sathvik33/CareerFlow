import { useState, useEffect } from 'react';
import api from '../services/api';
import { Save, User } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Profile() {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const { data } = await api.get('/users/me');
        setFormData({
          name: data.name || '',
          email: data.email || '',
          password: ''
        });
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const handleChange = (e, field) => {
    setFormData({ ...formData, [field]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');
    
    // Only send fields that are not empty
    const payload = {};
    if (formData.name) payload.name = formData.name;
    if (formData.email) payload.email = formData.email;
    if (formData.password) payload.password = formData.password;
    
    try {
      await api.put('/users/me', payload);
      setMessage('✅ Profile updated successfully!');
      // Reset password field after save
      setFormData(prev => ({ ...prev, password: '' }));
    } catch (err) {
      const detail = err.response?.data?.detail || 'Error updating profile';
      setMessage(`❌ ${detail}`);
    } finally {
      setSaving(false);
      setTimeout(() => setMessage(''), 4000);
    }
  };

  if (loading) return <div style={{padding: '40px'}}>Loading profile...</div>;

  return (
    <div className="animate-fade-in" style={styles.container}>
      <h1 style={styles.title}>Your Profile</h1>
      <p style={styles.subtitle}>Update your personal details and account credentials.</p>

      {message && <div style={styles.message}>{message}</div>}

      <form onSubmit={handleSubmit} className="glass-panel" style={styles.form}>
        <div style={styles.grid}>
          <div style={styles.inputGroup}>
            <label style={styles.label}>Full Name</label>
            <input 
              type="text" 
              value={formData.name} 
              onChange={(e) => handleChange(e, 'name')} 
              placeholder="e.g., John Doe"
              style={styles.input} 
            />
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>Email Address</label>
            <input 
              type="email" 
              value={formData.email} 
              onChange={(e) => handleChange(e, 'email')} 
              placeholder="you@example.com"
              style={styles.input} 
            />
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>New Password (leave blank to keep current)</label>
            <input 
              type="password" 
              value={formData.password} 
              onChange={(e) => handleChange(e, 'password')} 
              placeholder="••••••••"
              style={styles.input} 
            />
          </div>
        </div>

        <button type="submit" disabled={saving} style={styles.button}>
          <Save size={20} />
          {saving ? 'Updating...' : 'Update Profile'}
        </button>
      </form>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '600px',
  },
  title: {
    fontSize: '32px',
    marginBottom: '8px'
  },
  subtitle: {
    color: 'var(--text-secondary)',
    marginBottom: '32px'
  },
  message: {
    padding: '12px',
    backgroundColor: '#E8F6EF',
    color: '#27AE60',
    borderRadius: 'var(--radius-sm)',
    marginBottom: '24px',
    fontWeight: 500
  },
  form: {
    padding: '32px',
    display: 'flex',
    flexDirection: 'column',
    gap: '24px'
  },
  grid: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px'
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
    fontSize: '15px',
    outline: 'none',
    transition: 'border var(--transition-fast)'
  },
  button: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    padding: '14px 24px',
    backgroundColor: 'var(--primary)',
    color: '#FFF',
    border: 'none',
    borderRadius: 'var(--radius-sm)',
    fontSize: '16px',
    fontWeight: 600,
    cursor: 'pointer',
    alignSelf: 'flex-start',
    transition: 'background var(--transition-fast)'
  }
};
