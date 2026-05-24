import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline';
  fullWidth?: boolean;
}

export const Button: React.FC<ButtonProps> = ({ 
  children, 
  variant = 'primary', 
  fullWidth = false, 
  style, 
  ...props 
}) => {
  
  const baseStyle: React.CSSProperties = {
    padding: '0.75rem 1.5rem',
    borderRadius: '0.5rem',
    fontWeight: '600',
    fontSize: '1rem',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    border: 'none',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '0.5rem',
    width: fullWidth ? '100%' : 'auto',
    outline: 'none',
  };

  const variants = {
    primary: {
      background: 'linear-gradient(135deg, var(--primary), var(--secondary))',
      color: '#fff',
      boxShadow: 'var(--shadow-md)',
    },
    secondary: {
      background: 'var(--surface-color)',
      color: 'var(--text-primary)',
      border: '1px solid var(--border-color)',
    },
    outline: {
      background: 'transparent',
      color: 'var(--primary)',
      border: '2px solid var(--primary)',
    }
  };

  return (
    <button 
      style={{ ...baseStyle, ...variants[variant], ...style }} 
      onMouseOver={(e) => {
        if(variant === 'primary') {
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.boxShadow = 'var(--shadow-lg)';
        } else if (variant === 'secondary') {
          e.currentTarget.style.borderColor = 'var(--text-secondary)';
        }
      }}
      onMouseOut={(e) => {
        if(variant === 'primary') {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = 'var(--shadow-md)';
        } else if (variant === 'secondary') {
          e.currentTarget.style.borderColor = 'var(--border-color)';
        }
      }}
      {...props}
    >
      {children}
    </button>
  );
};
