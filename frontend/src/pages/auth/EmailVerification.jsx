import React, { useState, useEffect, useContext } from 'react';
import { useLocation, Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import MessageError from '../../components/messages/MessageError';
import MessageSuccess from '../../components/messages/MessageSuccess';

const EmailVerification = () => {
  const { baseUrl, refreshUserInfo, refreshToken } = useContext(AuthContext); 
  const [message, setMessage] = useState('');
  const [isError, setIsError] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [email, setEmail] = useState('');
  const location = useLocation();
  const navigate = useNavigate();

  const token = new URLSearchParams(location.search).get('token');

  useEffect(() => {
    if (!token) {
      setMessage('Verification token is missing.');
      setIsError(true);
      return;
    }

    const verifyEmail = async () => {
      try {
        const response = await fetch(`${baseUrl}/auth/verify-email?token=${token}`, {
          method: 'GET',
        });

        const data = await response.json();

        if (response.ok) {
          setMessage('Email verified successfully.');
          setEmail(data.email);
          setIsError(false);
          setShowSuccess(true);

          // Refresh token
          refreshToken(data.access_token);

          // Show success message for 2 seconds then redirect
          setTimeout(() => {
            setShowSuccess(false); 
            navigate('/signin');
          }, 2000);
        } else {
          setMessage(data.message || 'Email verification failed. Please try again.');
          setIsError(true);

          // Show error message for 2 seconds then redirect
          setTimeout(() => {
            navigate('/signin');
          }, 2000);
        }
      } catch (error) {
        setMessage('An error occurred during email verification.');
        setIsError(true);

        // Show error message for 2 seconds then redirect
        setTimeout(() => {
          navigate('/signin');
        }, 2000);
      }
    };

    verifyEmail();
  }, [token, baseUrl, refreshUserInfo, navigate, refreshToken]);

  return (
    <div className="form">
      <div className="form__box">
        {/* Conditional title based on success or failure */}
        <h2 className="form__title">
          {isError ? 'Verification Failed' : 'Email Verification'}
        </h2>

        {/* Show error message */}
        {isError ? (
          <>
            <MessageError message={message} />
          </>
        ) : (
          showSuccess && (
            <>
              <MessageSuccess message={message} />
              {email && <p>Email verified: {email}</p>}
            </>
          )
        )}
      </div>
    </div>
  );
};

export default EmailVerification;
