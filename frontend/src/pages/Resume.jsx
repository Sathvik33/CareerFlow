import { useState, useRef } from 'react';
import api from '../services/api';
import { UploadCloud, FileText } from 'lucide-react';

export default function Resume() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected && selected.type === 'application/pdf') {
      setFile(selected);
      setError('');
    } else {
      setFile(null);
      setError('Please upload a valid PDF file.');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const dropped = e.dataTransfer.files[0];
    if (dropped && dropped.type === 'application/pdf') {
      setFile(dropped);
      setError('');
    } else {
      setFile(null);
      setError('Please drop a valid PDF file.');
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    
    setUploading(true);
    setMessage('');
    setError('');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      await api.post('/resumes/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setMessage('Resume uploaded and processed successfully! Your skills have been embedded.');
      setFile(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred during upload.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="animate-fade-in" style={styles.container}>
      <h1 style={styles.title}>Resume Hub</h1>
      <p style={styles.subtitle}>Upload your latest resume to enhance your AI matching accuracy.</p>

      {message && <div style={styles.messageSuccess}>{message}</div>}
      {error && <div style={styles.messageError}>{error}</div>}

      <div 
        style={styles.dropZone}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input 
          type="file" 
          accept=".pdf" 
          ref={fileInputRef} 
          onChange={handleFileChange} 
          style={{ display: 'none' }} 
        />
        
        {file ? (
          <div style={styles.filePreview}>
            <FileText size={48} color="var(--primary)" />
            <p style={{ fontWeight: 600 }}>{file.name}</p>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        ) : (
          <div style={styles.uploadPrompt}>
            <UploadCloud size={48} color="var(--text-secondary)" />
            <p style={{ fontWeight: 600, fontSize: '18px' }}>Drag & drop your PDF here</p>
            <p style={{ color: 'var(--text-secondary)' }}>or click to browse files</p>
          </div>
        )}
      </div>

      <button 
        onClick={handleUpload} 
        disabled={!file || uploading} 
        style={{
          ...styles.button,
          opacity: (!file || uploading) ? 0.6 : 1,
          cursor: (!file || uploading) ? 'not-allowed' : 'pointer'
        }}
      >
        {uploading ? 'Processing Resume...' : 'Analyze Resume'}
      </button>
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
  dropZone: {
    border: '2px dashed var(--border-color)',
    borderRadius: 'var(--radius-lg)',
    padding: '60px 20px',
    textAlign: 'center',
    cursor: 'pointer',
    backgroundColor: 'rgba(255, 255, 255, 0.5)',
    transition: 'all var(--transition-fast)',
    marginBottom: '24px',
    minHeight: '250px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  },
  uploadPrompt: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '12px'
  },
  filePreview: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '8px'
  },
  messageSuccess: {
    padding: '16px',
    backgroundColor: '#E8F6EF',
    color: '#27AE60',
    borderRadius: 'var(--radius-sm)',
    marginBottom: '24px',
    fontWeight: 500
  },
  messageError: {
    padding: '16px',
    backgroundColor: '#FFEAEA',
    color: '#D8000C',
    borderRadius: 'var(--radius-sm)',
    marginBottom: '24px',
    fontWeight: 500
  },
  button: {
    width: '100%',
    padding: '16px',
    backgroundColor: 'var(--primary)',
    color: '#FFF',
    border: 'none',
    borderRadius: 'var(--radius-sm)',
    fontSize: '16px',
    fontWeight: 600,
    transition: 'background var(--transition-fast)'
  }
};
