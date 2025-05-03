import { useState, useEffect, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import PrimaryButton from '../../components/buttons/PrimaryButton';
import MessageError from '../../components/messages/MessageError';
import InputField from '../../components/forms/InputField';
import SecondaryButton from '../../components/buttons/SecondaryButton';

const UserProfileEdit = () => {
  const { baseUrl, token, userInfo, logout, updateUserInfo } = useContext(AuthContext);
  const [firstname, setFirstName] = useState(userInfo?.firstname || '');
  const [lastname, setLastName] = useState(userInfo?.lastname || '');
  const [email, setEmail] = useState(userInfo?.email || '');
  const [message, setMessage] = useState(''); 
  const navigate = useNavigate();

  useEffect(() => {
    if (!token) {
      setMessage('No token found. Please log in.');
      navigate('/signin');
    }
  }, [token, navigate]);

  useEffect(() => {
    const fetchUserInfo = async () => {
      if (!token) {
        setMessage('No token found. Please log in.');
        navigate('/signin');
        return;
      }

      try {
        const response = await fetch(`${baseUrl}/user`, {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) throw new Error('Failed to fetch user info.');

        const data = await response.json();
        setFirstName(data.User.firstname);
        setLastName(data.User.lastname);
        setEmail(data.User.email);
      } catch (error) {
        setMessage(error.message);
      }
    };

    if (!userInfo) fetchUserInfo();
  }, [baseUrl, token, userInfo, navigate]);

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
  
    try {
      const response = await fetch(`${baseUrl}/user`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ firstname, lastname, email }),
      });
  
      if (response.ok) {
        const data = await response.json();

        updateUserInfo(
          {
            firstname: data.firstname,
            lastname: data.lastname,
            email: data.email,
          },
          data.access_token
        );
  
        setMessage('Profile updated successfully.');
        navigate('/dashboard');
      } else {
        const data = await response.json();
  
        if (response.status === 400 && data.detail === "Email already exists") {
          setMessage("This email is already in use. Please choose another one.");
        } else {
          setMessage(data?.message || 'An error occurred.');
        }
      }
    } catch (error) {
      setMessage('Error updating profile.');
    }
  };

  return (
    <div className="form">
      <div className="form__box">
        <h2 className="form__title">Update Profile</h2>

        {message && <MessageError message={message} />}  

        <form onSubmit={handleUpdateProfile}>
          <InputField
            label="First Name"
            type="text"
            id="firstname"
            value={firstname}
            onChange={(e) => setFirstName(e.target.value)}
            required
          />
          <InputField
            label="Last Name"
            type="text"
            id="lastname"
            value={lastname}
            onChange={(e) => setLastName(e.target.value)}
            required
          />
          <InputField
            label="Email"
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <div className="form__button-group">
            <PrimaryButton type="submit">Update Profile</PrimaryButton>
            <SecondaryButton
              type="button"
              onClick={() => navigate('/password-edit')}
              fullWidth
            >
              Change Password
            </SecondaryButton>
          </div>
        </form>

        <div className="form__actions">
          <Link to="/dashboard" className="form__link">Cancel</Link>
          <Link
            to="/account-delete"
            className="form__link form__link--danger"
          >
            Delete Account
          </Link>
        </div>
      </div>
    </div>
  );
};

export default UserProfileEdit;
