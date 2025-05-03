// frontend/src/components/buttons/DangerButton.jsx
import React from 'react';

const DangerButton = ({ type, onClick, children, disabled }) => {
  return (
    <button 
      type={type} 
      className={`button button--danger ${disabled ? 'button--disabled' : ''}`} 
      onClick={onClick} 
      disabled={disabled}
    >
      {children}
    </button>
  );
};

export default DangerButton;
