// src/pages/auth/Signups.jsx
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import PrimaryButton from '../../components/buttons/PrimaryButton';
import SocialButton from '../../components/buttons/SocialButton';

const Signups = () => {
  const navigate = useNavigate();

  return (
    <div className="form">
      <div className="form__box">
        <h2 className="form__title">Sign Up</h2>
        <p className="form__subtitle">Select how you want to sign up:</p>
        <div className="form__button-group">
          {/* Go to the signup page */}
          <PrimaryButton onClick={() => navigate('/signup')}>Sign up with Email</PrimaryButton>
          <SocialButton provider="google" onClick={() => handleSocialSignin('google-oauth2')}>
              Sign Up with Google
          </SocialButton>
          <SocialButton provider="apple" onClick={() => handleSocialSignin('apple')}>
              Sign Up with Apple
          </SocialButton>
        </div>
        <div className="form__links">
          <Link to="/signin" className="form__link">Already have an account?</Link>
        </div>
      </div>
    </div>
  );
};

export default Signups;
