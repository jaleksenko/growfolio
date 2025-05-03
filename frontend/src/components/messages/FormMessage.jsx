// src/components/messages/FormMessage.jsx
import React from 'react';

const FormMessage = ({ message, isError }) => {
  if (!message) return null;

  const messageClass = isError ? 'message--error' : 'message--success';

  return (
    <div className={`message-container`}>
      <div className={`message ${messageClass}`} style={{ color: isError ? 'red' : 'black' }}>
        {message}
      </div>
    </div>
  );
};

export default FormMessage;


