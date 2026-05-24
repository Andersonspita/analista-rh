import React from 'react';

export const Card: React.FC<{ children: React.ReactNode; style?: React.CSSProperties, className?: string }> = ({ 
  children, 
  style,
  className = ''
}) => {
  return (
    <div 
      className={`glass ${className}`}
      style={{
        padding: '2rem',
        width: '100%',
        ...style
      }}
    >
      {children}
    </div>
  );
};
