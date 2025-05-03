// frontend/src/router/AppLayout.jsx
import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Navbar from '.././components/Navbar';

const AppLayout = () => {
  const location = useLocation();

  // Pages without Navbar
  const noNavbarRoutes = ['/signin', '/signup', '/signups'];
  const hideNavbar = noNavbarRoutes.includes(location.pathname);

  return (
    <div className="app-layout">
      {!hideNavbar && <Navbar />}
      <div className="app-content">
        <Outlet />
      </div>
    </div>
  );
};

export default AppLayout;

