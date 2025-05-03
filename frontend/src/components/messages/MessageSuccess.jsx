// src/components/messages/MessageSuccess.jsx
import React from 'react';

const MessageSuccess = ({ message }) => {
  if (!message) return null;

  return (
    <div className="message-container">
      <div className="message message--success">
        {message}
      </div>
    </div>
  );
};

export default MessageSuccess;


