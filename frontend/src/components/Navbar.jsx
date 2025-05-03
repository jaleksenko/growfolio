// frontend/src/components/Navbar.jsx
import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import Logo from '../assets/logo.svg';

const Navbar = () => {
  const { token, userInfo, logout } = useContext(AuthContext);

  return (
    <nav className="navbar">
      <div className="navbar__container">
        {/* Left: Logo */}
        <div className="navbar__left">
          <Link to={token ? "/dashboard" : "/"} className="navbar__logo" aria-label="Growfolio">
            <img src={Logo} alt="Growfolio" />
          </Link>
        </div>

        {/* Center: Authenticated nav links */}
        {token && (
          <div className="navbar__center">
            <Link to="/dashboard" className="navbar__link">Dashboard</Link>
            <Link to="/watchlist" className="navbar__link">Watchlist</Link>
            <Link to="/portfolio" className="navbar__link">Portfolio</Link>
          </div>
        )}

        {/* Right: User or Sign In */}
        <div className="navbar__right">
          {token && userInfo ? (
            <>
              <span className="navbar__user-info">
                {userInfo.firstname} {userInfo.lastname}
              </span>
              <Link to="/profile-edit" className="navbar__link">Edit Profile</Link>
              <button className="navbar__signout" onClick={logout}>Sign Out</button>
            </>
          ) : (
            <>
              <Link to="/signin" className="navbar__link">Sign In</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
