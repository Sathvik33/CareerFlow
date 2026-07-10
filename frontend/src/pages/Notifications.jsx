import { useState, useEffect } from 'react';
import api from '../services/api';
import { Bell, Plus, Trash2, Mail } from 'lucide-react';

export default function Notifications() {
  const [channels, setChannels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newEmail, setNewEmail] = useState('');
  const [adding, setAdding] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchChannels();
  }, []);

  const fetchChannels = async () => {
    try {
      const { data } = await api.get('/notifications/channels');
      setChannels(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddChannel = async (e) => {
    e.preventDefault();
    if (!newEmail) return;
    setAdding(true);
    setMessage('');
    setError('');

    try {
      await api.post('/notifications/channels', {
        channel: 'email',
        destination: newEmail,
        is_active: true
      });
      setMessage('Notification channel added successfully!');
      setNewEmail('');
      fetchChannels();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add channel.');
    } finally {
      setAdding(false);
    }
  };

  const handleToggle = async (id, currentStatus) => {
    try {
      await api.put(`/notifications/channels/${id}`, {
        is_active: !currentStatus
      });
      fetchChannels();
    } catch (err) {
      setError('Failed to update channel status.');
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/notifications/channels/${id}`);
      setMessage('Channel removed.');
      fetchChannels();
    } catch (err) {
      setError('Failed to remove channel.');
    }
  };

  if (loading) return <div style={{padding: '40px'}}>Loading settings...</div>;

  return (
    <div className="animate-fade-in" style={styles.container}>
      <h1 style={styles.title}>Notification Settings</h1>
      <p style={styles.subtitle}>Configure where you want to receive your daily intelligence reports.</p>

      {message && <div style={styles.messageSuccess}>{message}</div>}
      {error && <div style={styles.messageError}>{error}</div>}

      <div className="glass-panel" style={styles.card}>
        <h2 style={{ fontSize: '20px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Bell size={24} color="var(--primary)" />
          Your Channels
        </h2>

        {channels.length === 0 ? (
          <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
            No notification channels set. You will only see reports in your Dashboard.
          </p>
        ) : (
          <div style={styles.channelList}>
            {channels.map((ch) => (
              <div key={ch.id} style={styles.channelItem}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <Mail size={20} color="var(--text-secondary)" />
                  <div>
                    <strong style={{ display: 'block' }}>{ch.destination}</strong>
                    <span style={{ fontSize: '13px', color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{ch.channel}</span>
                  </div>
                </div>
                
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <label style={styles.toggleLabel}>
                    <input 
                      type="checkbox" 
                      checked={ch.is_active} 
                      onChange={() => handleToggle(ch.id, ch.is_active)}
                      style={styles.toggle}
                    />
                    {ch.is_active ? 'Active' : 'Paused'}
                  </label>
                  <button onClick={() => handleDelete(ch.id)} style={styles.deleteButton} title="Remove Channel">
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        <h3 style={{ fontSize: '16px', marginTop: '32px', marginBottom: '16px' }}>Add Email Destination</h3>
        <form onSubmit={handleAddChannel} style={styles.form}>
          <input 
            type="email" 
            value={newEmail} 
            onChange={(e) => setNewEmail(e.target.value)} 
            placeholder="e.g., jobs@example.com"
            style={styles.input}
            required
          />
          <button type="submit" disabled={adding || !newEmail} style={styles.button}>
            <Plus size={18} />
            {adding ? 'Adding...' : 'Add Channel'}
          </button>
        </form>
      </div>
    </div>
  );
}

const styles = {
  container: { maxWidth: '800px', paddingBottom: '40px' },
  title: { fontSize: '32px', marginBottom: '8px' },
  subtitle: { color: 'var(--text-secondary)', marginBottom: '32px' },
  card: { padding: '32px' },
  messageSuccess: { padding: '16px', backgroundColor: '#E8F6EF', color: '#27AE60', borderRadius: 'var(--radius-sm)', marginBottom: '24px', fontWeight: 500 },
  messageError: { padding: '16px', backgroundColor: '#FFEAEA', color: '#D8000C', borderRadius: 'var(--radius-sm)', marginBottom: '24px', fontWeight: 500 },
  channelList: { display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '32px' },
  channelItem: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px', backgroundColor: 'rgba(255,255,255,0.6)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' },
  toggleLabel: { display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '14px', color: 'var(--text-secondary)' },
  toggle: { accentColor: 'var(--primary)', width: '16px', height: '16px' },
  deleteButton: { background: 'none', border: 'none', color: '#E74C3C', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '8px', borderRadius: '4px', transition: 'background var(--transition-fast)' },
  form: { display: 'flex', gap: '12px' },
  input: { flex: 1, padding: '12px 16px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', outline: 'none', fontSize: '15px' },
  button: { display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '12px 24px', backgroundColor: 'var(--primary)', color: '#FFF', border: 'none', borderRadius: 'var(--radius-sm)', fontSize: '15px', fontWeight: 600, cursor: 'pointer', transition: 'background var(--transition-fast)' }
};
