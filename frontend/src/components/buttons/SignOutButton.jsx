// src/components/buttons/SignOutButton.jsx
import React from 'react';

const SignOutButton = ({ onClick }) => {
  return (
    <button onClick={onClick} className="button button--signout">
      Sign Out
    </button>
  );
};

export default SignOutButton;
