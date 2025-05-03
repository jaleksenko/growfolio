// src/components/messages/MessageError.jsx
import React from 'react';

const MessageError = ({ message }) => {
  if (!message) return null;

  return (
    <div className="message-container">
      <div className="message message--error">
        {message}
      </div>
    </div>
  );
};

export default MessageError;
