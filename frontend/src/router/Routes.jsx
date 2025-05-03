// src/router/AppRoutes.jsx
import React from 'react';
import { Routes, Route } from 'react-router-dom';

import { AuthContext } from '../context/AuthContext';

import AppLayout from './AppLayout';
import ProtectedRoute from './ProtectedRoute';

import HomePage from '../pages/HomePage';
import Signin from '../pages/auth/Signin';
import Signup from '../pages/auth/Signup';
import Signups from '../pages/auth/Signups';
import EmailVerification from '../pages/auth/EmailVerification';
import PasswordResetRequest from '../pages/auth/PasswordResetRequest';
import PasswordResetForm from '../pages/auth/PasswordResetForm';

import Dashboard from '../pages/Dashboard';
import Portfolio from '../components/dashboard/Portfolio';
import Watchlist from '../components/dashboard/Watchlist';
import UserProfileEdit from '../pages/auth/UserProfileEdit';
import UserPasswordEdit from '../pages/auth/UserPasswordEdit';
import AccountDeleteForm from '../pages/auth/AccountDeleteForm';

const AppRoutes = () => {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        {/* Public routes */}
        <Route path="/" element={<HomePage />} />
        <Route path="/signin" element={<Signin />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/signups" element={<Signups />} />
        <Route path="/verify-email" element={<EmailVerification />} />
        <Route path="/password-reset" element={<PasswordResetRequest />} />
        <Route path="/password-reset-form" element={<PasswordResetForm />} />

        {/* Protected routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/portfolio"
          element={
            <ProtectedRoute>
              <Portfolio />
            </ProtectedRoute>
          }
        />
        <Route
          path="/watchlist"
          element={
            <ProtectedRoute>
              <Watchlist />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile-edit"
          element={
            <ProtectedRoute>
              <UserProfileEdit />
            </ProtectedRoute>
          }
        />
        <Route
          path="/password-edit"
          element={
            <ProtectedRoute>
              <UserPasswordEdit />
            </ProtectedRoute>
          }
        />
        <Route
          path="/account-delete"
          element={
            <ProtectedRoute>
              <AccountDeleteForm />
            </ProtectedRoute>
          }
        />
      </Route>
    </Routes>
  );
};

export default AppRoutes;
