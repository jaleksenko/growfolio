import { useState, useContext } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import SecondaryButton from '../../components/buttons/SecondaryButton';
import FormMessage from '../../components/messages/FormMessage';
import MessageSuccess from '../../components/messages/MessageSuccess';
import { AuthContext } from '../../context/AuthContext';

const PasswordResetForm = () => {
  const { baseUrl } = useContext(AuthContext);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [messageError, setMessageError] = useState('');
  const [passwordValid, setPasswordValid] = useState({
    length: false,
    digit: false,
    specialChar: false,
  });
  const [passwordMismatch, setPasswordMismatch] = useState(false);
  const [isFormValid, setIsFormValid] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const token = new URLSearchParams(location.search).get('token');

  // Password validation logic
  const validatePassword = (password) => ({
    length: password.length >= 8,
    digit: /\d/.test(password),
    specialChar: /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]+/.test(password),
  });

  // Handle new password change
  const handlePasswordChange = (e) => {
    const value = e.target.value;
    setNewPassword(value);

    const validation = validatePassword(value);
    setPasswordValid(validation);

    if (confirmPassword && value !== confirmPassword) {
      setPasswordMismatch(true);
    } else {
      setPasswordMismatch(false);
    }

    const isValid = Object.values(validation).every(Boolean);
    setIsFormValid(isValid && value === confirmPassword);
  };

  // Handle confirm password change
  const handleConfirmPasswordChange = (e) => {
    const value = e.target.value;
    setConfirmPassword(value);

    if (newPassword !== value) {
      setPasswordMismatch(true);
    } else {
      setPasswordMismatch(false);
      setMessageError(''); // Clear error
    }

    setIsFormValid(passwordValid.length && passwordValid.digit && passwordValid.specialChar && value === newPassword);
  };

  const handlePasswordReset = async (e) => {
    e.preventDefault();

    if (passwordMismatch) {
      setMessageError('Passwords do not match. Please try again.');
      return;
    }
    if (!token) {
      setMessageError('Invalid or missing token.');
      return;
    }
    if (!isFormValid) {
      setMessageError('Please ensure the password meets all requirements.');
      return;
    }

    try {
      const response = await fetch(`${baseUrl}/auth/password-reset-form`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token, newPassword }),
      });

      const data = await response.json();
      if (response.ok) {
        setIsSuccess(true);
        setMessageError(''); 

        // Redirect
        setTimeout(() => {
          navigate('/signin');
        }, 2000);
      } else if (response.status === 400 && data.detail === "New password must be different from the old password.") {
        setMessageError(data.detail);
      } else {
        setMessageError(data.detail || 'An error occurred. Please try again.');
      }
    } catch (error) {
      setMessageError('Failed to reset password. Please try again later.');
    }
  };

  // If Success
  if (isSuccess) {
    return (
      <div className="form">
        <div className="form__box">
        <h3 className="form__title">Reset Successful</h3>
          <MessageSuccess message="Your password has been reset successfully." />
        </div>
      </div>
    );
  }

  return (
    <div className="form">
      <div className="form__box">
        <h2 className="form__title">Reset Password</h2>
        
        
        {/* Error message in red */}
        <FormMessage message={messageError || (passwordMismatch && "Passwords do not match.")} isError={true} />
        
        <form onSubmit={handlePasswordReset}>
          <div className="form__group">
            <label htmlFor="newPassword">New Password</label>
            <input
              type="password"
              id="newPassword"
              value={newPassword}
              onChange={handlePasswordChange}
              required
            />
            {/* Password validation */}
            {!passwordMismatch && (
              <div className="validation">
                <p className="validation__text">Your password must meet the following requirements:</p>
                <ul className="validation__list">
                  <li className={`validation__item ${passwordValid.length ? 'valid' : 'invalid'}`}>At least 8 characters long</li>
                  <li className={`validation__item ${passwordValid.digit ? 'valid' : 'invalid'}`}>At least one digit</li>
                  <li className={`validation__item ${passwordValid.specialChar ? 'valid' : 'invalid'}`}>
                    At least one special character (e.g., !@#$%^&*)
                  </li>
                </ul>
              </div>
            )}
          </div>
          <div className="form__group">
            <label htmlFor="confirmPassword">Confirm New Password</label>
            <input
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={handleConfirmPasswordChange}
              required
            />
          </div>
          {passwordMismatch && (
            <p className="error">Passwords do not match.</p>
          )}
          <SecondaryButton type="submit" disabled={!isFormValid || passwordMismatch}>
            Reset Password
          </SecondaryButton>
        </form>
        <div className="form__links">
          <Link to="/signin" className="form__link">Cancel</Link>
        </div>
      </div>
    </div>
  );
};

export default PasswordResetForm;
