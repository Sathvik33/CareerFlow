import { useState, useEffect } from 'react';
import api from '../services/api';
import { Save } from 'lucide-react';

export default function Preferences() {
  const [formData, setFormData] = useState({
    roles: [],
    locations: [],
    experience_level: 'fresher',
    job_types: [],
    work_modes: [],
    preferred_skills: [],
    salary_min: 0,
    salary_max: 0
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchPreferences();
  }, []);

  const [roleInput, setRoleInput] = useState('');
  const [locationInput, setLocationInput] = useState('');
  const [skillInput, setSkillInput] = useState('');

  const fetchPreferences = async () => {
    try {
      const { data } = await api.get('/preferences/');
      setFormData(data);
      if (data.roles) setRoleInput(data.roles.join(', '));
      if (data.locations) setLocationInput(data.locations.join(', '));
      if (data.preferred_skills) setSkillInput(data.preferred_skills.join(', '));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e, field) => {
    let value = e.target.value;
    if (field === 'salary_min' || field === 'salary_max') {
      value = parseInt(value) || 0;
    }
    setFormData({ ...formData, [field]: value });
  };

  const handleCheckboxChange = (field, option) => {
    const currentList = formData[field] || [];
    if (currentList.includes(option)) {
      setFormData({ ...formData, [field]: currentList.filter(item => item !== option) });
    } else {
      setFormData({ ...formData, [field]: [...currentList, option] });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');
    try {
      const payload = {
        ...formData,
        roles: roleInput.split(',').map(v => v.trim()).filter(Boolean),
        locations: locationInput.split(',').map(v => v.trim()).filter(Boolean),
        preferred_skills: skillInput.split(',').map(v => v.trim()).filter(Boolean)
      };
      await api.put('/preferences/', payload);
      setMessage('✅ Preferences saved successfully!');
    } catch (err) {
      const detail = err.response?.data?.detail || 'Error saving preferences';
      setMessage(`❌ ${detail}`);
    } finally {
      setSaving(false);
      // Clear message after 4 seconds
      setTimeout(() => setMessage(''), 4000);
    }
  };

  if (loading) return <div style={{padding: '40px'}}>Loading preferences...</div>;

  return (
    <div className="animate-fade-in" style={styles.container}>
      <h1 style={styles.title}>Job Preferences</h1>
      <p style={styles.subtitle}>Tell us what you're looking for, and our AI will find the best matches.</p>

      {message && <div style={styles.message}>{message}</div>}

      <form onSubmit={handleSubmit} className="glass-panel" style={styles.form}>
        <div style={styles.grid}>
          <div style={styles.inputGroup}>
            <label style={styles.label}>Target Roles (comma separated)</label>
            <input 
              type="text" 
              value={roleInput} 
              onChange={(e) => setRoleInput(e.target.value)} 
              placeholder="e.g., Software Engineer, Data Scientist"
              style={styles.input} 
            />
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>Experience Level</label>
            <select 
              value={formData.experience_level} 
              onChange={(e) => handleChange(e, 'experience_level')}
              style={styles.input}
            >
              <option value="student">Student</option>
              <option value="fresher">Fresher</option>
              <option value="junior">Junior</option>
              <option value="mid">Mid-Level</option>
              <option value="senior">Senior</option>
            </select>
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>Locations (comma separated)</label>
            <input 
              type="text" 
              value={locationInput} 
              onChange={(e) => setLocationInput(e.target.value)} 
              placeholder="e.g., New York, San Francisco"
              style={styles.input} 
            />
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>Preferred Skills</label>
            <input 
              type="text" 
              value={skillInput} 
              onChange={(e) => setSkillInput(e.target.value)} 
              placeholder="e.g., Python, React, PostgreSQL"
              style={styles.input} 
            />
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>Minimum Salary (USD)</label>
            <input 
              type="number" 
              value={formData.salary_min} 
              onChange={(e) => handleChange(e, 'salary_min')} 
              style={styles.input} 
            />
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>Maximum Salary (USD)</label>
            <input 
              type="number" 
              value={formData.salary_max} 
              onChange={(e) => handleChange(e, 'salary_max')} 
              style={styles.input} 
            />
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>Job Types</label>
            <div style={styles.checkboxGroup}>
              {['full_time', 'part_time', 'contract', 'internship'].map(type => (
                <label key={type} style={styles.checkboxLabel}>
                  <input 
                    type="checkbox" 
                    checked={(formData.job_types || []).includes(type)}
                    onChange={() => handleCheckboxChange('job_types', type)}
                    style={styles.checkbox}
                  />
                  {type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </label>
              ))}
            </div>
          </div>

          <div style={styles.inputGroup}>
            <label style={styles.label}>Work Modes</label>
            <div style={styles.checkboxGroup}>
              {['remote', 'hybrid', 'onsite'].map(mode => (
                <label key={mode} style={styles.checkboxLabel}>
                  <input 
                    type="checkbox" 
                    checked={(formData.work_modes || []).includes(mode)}
                    onChange={() => handleCheckboxChange('work_modes', mode)}
                    style={styles.checkbox}
                  />
                  {mode.charAt(0).toUpperCase() + mode.slice(1)}
                </label>
              ))}
            </div>
          </div>
        </div>

        <button type="submit" disabled={saving} style={styles.button}>
          <Save size={20} />
          {saving ? 'Saving...' : 'Save Preferences'}
        </button>
      </form>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '800px',
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
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
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
  },
  checkboxGroup: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '16px',
    padding: '8px 0'
  },
  checkboxLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '15px',
    cursor: 'pointer',
    color: 'var(--text-secondary)'
  },
  checkbox: {
    width: '18px',
    height: '18px',
    cursor: 'pointer',
    accentColor: 'var(--primary)'
  }
};
