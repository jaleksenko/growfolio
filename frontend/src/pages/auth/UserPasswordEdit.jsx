import { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom'; 
import { AuthContext } from '../../context/AuthContext';
import SecondaryButton from '../../components/buttons/SecondaryButton';
import InputField from '../../components/forms/InputField';
import FormMessage from '../../components/messages/FormMessage';

const UserPasswordEdit = () => {
  const { baseUrl, setToken, refreshUserInfo } = useContext(AuthContext);  // Access context values
  const [currentPassword, setCurrentPassword] = useState('');  // State for current password
  const [newPassword, setNewPassword] = useState('');  // State for new password
  const [confirmNewPassword, setConfirmNewPassword] = useState('');  // State for confirm password
  const [messageError, setMessageError] = useState('');  // Error message state
  const [passwordValid, setPasswordValid] = useState({
    length: false,
    digit: false,
    specialChar: false,
  });  // State for password validation rules
  const [passwordMismatch, setPasswordMismatch] = useState(false);  // State for password mismatch
  const [isFormValid, setIsFormValid] = useState(false);  // Form validity state
  const navigate = useNavigate();  // Hook for navigation

  // Password validation function
  const validatePassword = (password) => ({
    length: password.length >= 8,
    digit: /\d/.test(password),
    specialChar: /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]+/.test(password),
  });

  // Handle new password change
  const handleNewPasswordChange = (e) => {
    const value = e.target.value;
    setNewPassword(value);

    const validation = validatePassword(value);
    setPasswordValid(validation);

    if (confirmNewPassword && value !== confirmNewPassword) {
      setPasswordMismatch(true);
    } else {
      setPasswordMismatch(false);
    }

    const isValid = Object.values(validation).every(Boolean);
    setIsFormValid(isValid && value === confirmNewPassword);
  };

  // Handle confirm new password
  const handleConfirmPasswordChange = (e) => {
    const value = e.target.value;
    setConfirmNewPassword(value);

    if (newPassword !== value) {
      setPasswordMismatch(true);
    } else {
      setPasswordMismatch(false);
      setMessageError(''); // Clear error
    }

    setIsFormValid(passwordValid.length && passwordValid.digit && passwordValid.specialChar && value === newPassword);
  };

  // Handle password change submission
  const handlePasswordChange = async (e) => {
    e.preventDefault();

    if (passwordMismatch) {
      setMessageError('New passwords do not match.');
      return;
    }

    const token = localStorage.getItem('token');
    const response = await fetch(`${baseUrl}/auth/password-change`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      // Update token and user info
      setToken(data.access_token);
      localStorage.setItem('token', data.access_token);
      await refreshUserInfo();

      // Clear the form
      setCurrentPassword('');
      setNewPassword('');
      setConfirmNewPassword('');

      // Redirect to /signin immediately after success
      navigate('/signin');
    } else {
      setMessageError(data.detail || 'Failed to change password.');
    }
  };

  return (
    <div className="form">
      <div className="form__box">
        <h2 className="form__title">Change Password</h2>

        {/* Error message in red */}
        <FormMessage message={messageError || (passwordMismatch && "Passwords do not match.")} isError={true} />

        {/* Password change form */}
        <form onSubmit={handlePasswordChange}>
          <InputField
            label="Current Password"
            type="password"
            id="currentPassword"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            required
          />
          <InputField
            label="New Password"
            type="password"
            id="newPassword"
            value={newPassword}
            onChange={handleNewPasswordChange}
            required
          />
          <InputField
            label="Confirm New Password"
            type="password"
            id="confirmNewPassword"
            value={confirmNewPassword}
            onChange={handleConfirmPasswordChange}
            required
          />

          {/* Password validation */}
          {!passwordMismatch && (
            <div className="validation">
              <p className="validation__text">Your password must meet the following requirements:</p>
              <ul className="validation__list">
                <li className={`validation__item ${passwordValid.length ? 'valid' : 'invalid'}`}>
                  At least 8 characters long
                </li>
                <li className={`validation__item ${passwordValid.digit ? 'valid' : 'invalid'}`}>
                  At least one digit
                </li>
                <li className={`validation__item ${passwordValid.specialChar ? 'valid' : 'invalid'}`}>
                  At least one special character (e.g., !@#$%^&*)
                </li>
              </ul>
            </div>
          )}

          <SecondaryButton type="submit" disabled={!isFormValid || passwordMismatch} fullWidth>
            Change Password
          </SecondaryButton>
        </form>

        <div className="form__links">
          <Link to="/dashboard" className="form__link">Cancel</Link>
        </div>
      </div>
    </div>
  );
};

export default UserPasswordEdit;
