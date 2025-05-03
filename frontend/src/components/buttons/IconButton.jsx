// src/components/buttons/IconButton.jsx
import React from 'react';

const IconButton = ({ type, onClick, icon: Icon, children }) => {
  return (
    <button type={type} className="button button--icon" onClick={onClick}>
      {Icon && <Icon className="button__icon" />} {children}
    </button>
  );
};

export default IconButton;


