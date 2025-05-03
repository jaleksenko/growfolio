import { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import SecondaryButton from '../../components/buttons/SecondaryButton';
import MessageError from '../../components/messages/MessageError';
import MessageSuccess from '../../components/messages/MessageSuccess';

const PasswordResetRequest = () => {
  const { baseUrl } = useContext(AuthContext);
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isError, setIsError] = useState(false);
  const navigate = useNavigate();

  const handlePasswordResetReq = async (e) => {
    e.preventDefault();

    const trimmedEmail = email.trim();

    const response = await fetch(`${baseUrl}/auth/password-reset`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email: trimmedEmail }),
    });

    const data = await response.json();

    if (response.ok) {
      // Bold style foe email
      setMessage(`Password reset link has been sent to your email: <strong>${trimmedEmail}</strong>. Please check your inbox.`);
      setIsSubmitted(true);
      setIsError(false);

      // Redirect
      setTimeout(() => {
        navigate('/signin');
      }, 2000); 
    } else {
      setMessage(data.detail || 'An error occurred. Please try again.');
      setIsError(true);
    }
  };

  return (
    <div className="form">
      <div className="form__box">
        <h2 className="form__title">Password Reset</h2>

        {isSubmitted ? (
          <div className="message-container">
            <MessageSuccess message={<span>Password reset link has been sent to your email: <strong>{email}</strong>. Please check your inbox.</span>} />
            {/* <div className="form__links">
              <Link to="/signin" className="form__link">Return to Sign In</Link>
            </div> */}
          </div>
        ) : (
          <form onSubmit={handlePasswordResetReq}>
            <div className="form__group">
              <label htmlFor="email">Enter your email address:</label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <SecondaryButton type="submit">Send Reset Link</SecondaryButton>
          </form>
        )}

        {message && !isSubmitted && (
          isError ? <MessageError message={message} /> : <MessageSuccess message={message} />
        )}

        {/* Link to return */}
        <div className="form__links">
          <Link to="/signin" className="form__link">Cancel</Link>
        </div>
      </div>
    </div>
  );
};

export default PasswordResetRequest;

