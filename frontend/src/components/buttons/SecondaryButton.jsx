// frontend/src/components/buttons/SecondaryButton.jsx
import React from 'react';

const SecondaryButton = ({ type, onClick, children, disabled }) => {
  return (
    <button 
      type={type} 
      className={`button button--secondary ${disabled ? 'button--disabled' : ''}`} 
      onClick={onClick} 
      disabled={disabled}
    >
      {children}
    </button>
  );
};

export default SecondaryButton;
