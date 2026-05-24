import React from 'react';
import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

export const ThemeToggle: React.FC<{ className?: string }> = ({ className = '' }) => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className={`theme-toggle ${className}`}
      aria-label="Toggle Theme"
      style={{
        background: 'transparent',
        border: 'none',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'var(--text-primary)',
        padding: '0.5rem',
        borderRadius: '50%',
        transition: 'background-color 0.2s'
      }}
      onMouseOver={(e) => (e.currentTarget.style.backgroundColor = 'var(--border-color)')}
      onMouseOut={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
    >
      {theme === 'light' ? (
        <Moon size={24} />
      ) : (
        <Sun size={24} />
      )}
    </button>
  );
};
