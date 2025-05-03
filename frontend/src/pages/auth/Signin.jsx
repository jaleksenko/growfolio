import { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import PrimaryButton from '../../components/buttons/PrimaryButton';
import SocialButton from '../../components/buttons/SocialButton';
import InputField from '../../components/forms/InputField';
import MessageError from '../../components/messages/MessageError';
import MessageSuccess from '../../components/messages/MessageSuccess';

const Signin = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSignin = async (e) => {
    e.preventDefault();

    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const result = await login(formData);

      if (result && result.success) {
        // Successful login
        setMessage('Login successful.');
        setMessageType('success');
        setTimeout(() => {
          navigate('/dashboard');
        }, 3000); // Show the success message for 3 seconds before redirecting
      } else {
        // Error handling
        if (result.status === 403 && result.message.includes("Email not verified")) {
          setMessage(result.message); // Show email verification message
          setMessageType('success'); // Display as a success since email was sent
        } else if (result.status === 401) {
          setMessage('Invalid username or password. Please try again.');
          setMessageType('error');
        } else {
          setMessage('Login failed. Please try again later.');
          setMessageType('error');
        }
      }
    } catch (error) {
      setMessage('Login failed due to a server error.');
      setMessageType('error');
      console.log(error);
    }
  };

  return (
    <div className="form">
      <div className="form__box">
        <h2 className="form__title">Sign In</h2>

        {/* Display error or success message depending on the type */}
        {message && (
          messageType === 'error' ? (
            <div className="message message--error">{message}</div>
          ) : (
            <div className="message message--success">{message}</div>
          )
        )}

        <form onSubmit={handleSignin}>
          <InputField
            label="Username"
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <InputField
            label="Password"
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <div className="form__button-group">
            <PrimaryButton type="submit">Sign In</PrimaryButton>
            <SocialButton provider="google" onClick={() => handleSocialSignin('google-oauth2')}>
              Sign In with Google
            </SocialButton>
            <SocialButton provider="apple" onClick={() => handleSocialSignin('apple')}>
              Sign In with Apple
            </SocialButton>
          </div>
        </form>

        <div className="form__links">
          <Link to="/password-reset" className="form__link">Reset password</Link>
          <Link to="/signups" className="form__link">Don't have an account?</Link>
        </div>
      </div>
    </div>
  );
};

export default Signin;
