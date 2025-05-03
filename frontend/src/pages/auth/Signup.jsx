import { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import PrimaryButton from '../../components/buttons/PrimaryButton';
import InputField from '../../components/forms/InputField';
import FormMessage from '../../components/messages/FormMessage';

const Signup = () => {
  const { baseUrl } = useContext(AuthContext);
  const [username, setUsername] = useState('');
  const [firstname, setFirstName] = useState('');
  const [lastname, setLastName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [email, setEmail] = useState('');
  const [messageError, setMessageError] = useState('');
  const [messageSuccess, setMessageSuccess] = useState('');
  const [passwordValid, setPasswordValid] = useState({
    length: false,
    digit: false,
    specialChar: false,
  });
  const [isFormValid, setIsFormValid] = useState(false);
  const [showModal, setShowModal] = useState(false); // State for modal window
  const [passwordMismatch, setPasswordMismatch] = useState(false); // Flag for password mismatch
  const navigate = useNavigate();

  // Password validation logic
  const validatePassword = (password) => ({
    length: password.length >= 8,
    digit: /\d/.test(password),
    specialChar: /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]+/.test(password),
  });

  // Handle form submission
  const handleSignup = async (e) => {
    e.preventDefault();

    // Check for password mismatch
    if (passwordMismatch) {
      setMessageError('Passwords do not match. Please try again.');
      return;
    }

    // API request for user signup
    const response = await fetch(`${baseUrl}/auth`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, firstname, lastname, email, password }),
    });

    const data = await response.json();

    if (response.ok) {
      // Show modal with success message and bold email
      setShowModal(true);
      setMessageSuccess(
        <>
          A verification email has been sent to <strong>{email}</strong>. Please check your inbox.
        </>
      );
      
      // Hide modal after 3 seconds and redirect to sign-in page
      setTimeout(() => {
        navigate('/signin'); // Redirect to sign-in after 3 seconds
      }, 3000); 
    } else {
      setMessageError(data.detail || 'Signup failed. Please try again.');
    }
  };

  // Handle password change
  const handlePasswordChange = (e) => {
    const value = e.target.value;
    setPassword(value);

    const validation = validatePassword(value);
    setPasswordValid(validation);

    // Check for password mismatch
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

    // Check for password mismatch
    if (password !== value) {
      setPasswordMismatch(true);
    } else {
      setPasswordMismatch(false);
      setMessageError(''); // Clear error
    }

    setIsFormValid(passwordValid.length && passwordValid.digit && passwordValid.specialChar && value === password);
  };

  return (
    <div className="form">
      {/* Show modal when email is successfully sent */}
      {showModal && (
        <div className="form__box modal">
          <h2 className="form__title">Email Sent</h2>
          <FormMessage message={messageSuccess} isError={false} />
          <div className="form__links">
            <Link to="/signin" className="form__link">Go to Sign In</Link>
          </div>
        </div>
      )}

      {/* Hide the form when modal is active */}
      {!showModal && (
        <div className="form__box">
          <h2 className="form__title">Sign Up</h2>

          {/* Error message in red */}
          <FormMessage message={messageError || (passwordMismatch && "Passwords do not match.")} isError={true} />

          {/* Signup form */}
          <form onSubmit={handleSignup}>
            <InputField
              label="Username"
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <InputField
              label="First Name"
              type="text"
              id="firstname"
              value={firstname}
              onChange={(e) => setFirstName(e.target.value)}
            />
            <InputField
              label="Last Name"
              type="text"
              id="lastname"
              value={lastname}
              onChange={(e) => setLastName(e.target.value)}
            />
            <InputField
              label="Email"
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <InputField
              label="Password"
              type="password"
              id="password"
              value={password}
              onChange={handlePasswordChange}
            />
            <InputField
              label="Confirm Password"
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={handleConfirmPasswordChange}
            />

            {/* Show password validation */}
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

            {/* Submit button */}
            <PrimaryButton type="submit" disabled={!isFormValid || passwordMismatch} fullWidth>Sign Up</PrimaryButton>
          </form>

          {/* Link to sign-in */}
          <div className="form__links">
            <Link to="/signin" className="form__link">Already have an account?</Link>
          </div>
        </div>
      )}
    </div>
  );
};

export default Signup;