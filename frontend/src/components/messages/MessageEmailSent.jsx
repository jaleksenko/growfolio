// src/components/messages/MessageEmailSent.jsx
import React from 'react';
import { Link } from 'react-router-dom';

const MessageEmailSent = ({ email, onResend }) => {
  return (
    <div className="message message--info">
      <p>An email has been sent to <strong>{email}</strong>. Please check your inbox.</p>
      <button onClick={onResend} className="message__button">Resend Email</button>
      <div className="message__links">
        <Link to="/signin" className="message__link">Go to Sign In</Link>
      </div>
    </div>
  );
};

export default MessageEmailSent;
