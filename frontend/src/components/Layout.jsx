import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LayoutDashboard, Settings, FileText, LogOut, Bell, Briefcase } from 'lucide-react';

export default function Layout() {
  const { logout } = useAuth();
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/jobs', label: 'Job Matches', icon: Briefcase },
    { path: '/resume', label: 'Resume Hub', icon: FileText },
    { path: '/preferences', label: 'Preferences', icon: Settings },
    { path: '/notifications', label: 'Notifications', icon: Bell }
  ];

  return (
    <div style={styles.container}>
      <aside className="glass-panel" style={styles.sidebar}>
        <div style={styles.logo}>CareerFlow AI</div>
        <nav style={styles.nav}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = location.pathname.startsWith(item.path);
            return (
              <Link 
                key={item.path} 
                to={item.path} 
                style={{
                  ...styles.navItem,
                  ...(active ? styles.navItemActive : {})
                }}
              >
                <Icon size={20} />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <button onClick={logout} style={styles.logoutBtn}>
          <LogOut size={20} /> Logout
        </button>
      </aside>
      
      <main style={styles.main}>
        <Outlet />
      </main>
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    minHeight: '100vh',
    background: 'radial-gradient(circle at top left, #FDFBF7 0%, #EAE6DF 100%)',
  },
  sidebar: {
    width: '260px',
    margin: '20px',
    padding: '24px',
    display: 'flex',
    flexDirection: 'column',
    position: 'sticky',
    top: '20px',
    height: 'calc(100vh - 40px)',
  },
  logo: {
    fontSize: '22px',
    fontWeight: 700,
    color: 'var(--text-primary)',
    marginBottom: '40px',
    padding: '0 12px',
    letterSpacing: '-0.5px'
  },
  nav: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    flex: 1
  },
  navItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '12px 16px',
    borderRadius: 'var(--radius-sm)',
    color: 'var(--text-secondary)',
    fontWeight: 500,
    transition: 'all var(--transition-fast)'
  },
  navItemActive: {
    background: 'var(--gradient-positive)',
    color: 'var(--text-primary)',
    boxShadow: 'var(--shadow-sm)'
  },
  logoutBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '12px 16px',
    background: 'transparent',
    border: 'none',
    color: '#D8000C',
    fontWeight: 500,
    cursor: 'pointer',
    borderRadius: 'var(--radius-sm)',
    transition: 'background var(--transition-fast)',
    fontSize: '16px'
  },
  main: {
    flex: 1,
    padding: '20px 40px 20px 20px',
    overflowY: 'auto'
  }
};
