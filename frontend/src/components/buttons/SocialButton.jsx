// src/components/buttons/SocialButton.jsx
import React from 'react';
import { FaGoogle, FaApple } from 'react-icons/fa';

const SocialButton = ({ type, onClick, provider, children }) => {
  const Icon = provider === 'google' ? FaGoogle : provider === 'apple' ? FaApple : null;

  return (
    <button type={type} className={`button button--${provider}`} onClick={onClick}>
      {Icon && <Icon className="button__icon" />} {children}
    </button>
  );
};

export default SocialButton;

