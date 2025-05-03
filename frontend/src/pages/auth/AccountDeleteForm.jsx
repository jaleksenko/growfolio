import { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import DangerButton from '../../components/buttons/DangerButton';
import InputField from '../../components/forms/InputField';
import FormMessage from '../../components/messages/FormMessage';

const AccountDeleteForm = () => {
  const [password, setPassword] = useState('');
  const [messageError, setMessageError] = useState('');
  const { baseUrl, token, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!password) {
      setMessageError('Password is required to delete the account.');
      return;
    }

    try {
      const response = await fetch(`${baseUrl}/user`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password }),
      });

      if (response.ok) {
        logout();
        navigate('/'); // Redirect to homepage after account deletion
      } else {
        const data = await response.json();
        setMessageError(data.detail || 'Failed to delete account.');
      }
    } catch (error) {
      setMessageError('Error deleting account.');
    }
  };

  return (
    <div className="form">
      <div className="form__box">
        <h2 className="form__title">Confirm Deletion</h2>

        <FormMessage message="This action will permanently delete your account and all associated data." isError={true} />

        {messageError && <FormMessage message={messageError} isError={true} />}

        <form onSubmit={handleSubmit}>
          <InputField
            label="Password"
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <div className="form__button-group">
            <DangerButton type="submit" fullWidth>Delete Account</DangerButton>
            <div className="form__links">
              <Link to="/dashboard" className="form__link">Cancel</Link>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AccountDeleteForm;
