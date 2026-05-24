import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, style, id, ...props }, ref) => {
    
    const containerStyle: React.CSSProperties = {
      display: 'flex',
      flexDirection: 'column',
      gap: '0.5rem',
      width: '100%',
      marginBottom: '1rem',
    };

    const labelStyle: React.CSSProperties = {
      fontSize: '0.875rem',
      fontWeight: '500',
      color: 'var(--text-primary)',
    };

    const inputStyle: React.CSSProperties = {
      width: '100%',
      padding: '0.75rem 1rem',
      borderRadius: '0.5rem',
      border: `1px solid ${error ? '#ef4444' : 'var(--border-color)'}`,
      background: 'var(--surface-color)',
      color: 'var(--text-primary)',
      fontSize: '1rem',
      outline: 'none',
      transition: 'border-color 0.2s, box-shadow 0.2s',
    };

    const errorStyle: React.CSSProperties = {
      fontSize: '0.75rem',
      color: '#ef4444',
      marginTop: '-0.25rem',
    };

    return (
      <div style={containerStyle}>
        {label && <label htmlFor={id} style={labelStyle}>{label}</label>}
        <input
          ref={ref}
          id={id}
          style={{ ...inputStyle, ...style }}
          onFocus={(e) => {
            if (!error) {
              e.currentTarget.style.borderColor = 'var(--primary)';
              e.currentTarget.style.boxShadow = '0 0 0 3px rgba(79, 70, 229, 0.2)';
            }
          }}
          onBlur={(e) => {
            if (!error) {
              e.currentTarget.style.borderColor = 'var(--border-color)';
              e.currentTarget.style.boxShadow = 'none';
            }
          }}
          {...props}
        />
        {error && <span style={errorStyle}>{error}</span>}
      </div>
    );
  }
);

Input.displayName = 'Input';
