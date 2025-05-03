import React, { createContext, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem("token") || null);
  const [userInfo, setUserInfo] = useState(null);
  const baseUrl = import.meta.env.VITE_BASE_URL;
  const navigate = useNavigate();
  const hasFetched = useRef(false);

  const fetchUserInfo = async (accessToken) => {
    if (!accessToken) return;

    try {
      const response = await fetch(`${baseUrl}/user`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) throw new Error("Failed to fetch user info");

      const data = await response.json();

      if (!data || !data.username) throw new Error("Invalid user data");

      setUserInfo({
        username: data.username,
        firstname: data.firstname,
        lastname: data.lastname,
        email: data.email,
      });
    } catch (error) {
      console.error("Error fetching user info:", error);
    }
  };

  // Initial fetch if token exists and not already fetched
  useEffect(() => {
    if (token && !hasFetched.current) {
      fetchUserInfo(token);
      hasFetched.current = true;
    }
  }, [token]);

  // Called after login or refresh
  const refreshToken = (newToken) => {
    setToken(newToken);
    localStorage.setItem("token", newToken);
    fetchUserInfo(newToken);
  };

  const updateUserInfo = (newUserInfo, newToken = null) => {
    setUserInfo(newUserInfo);
    if (newToken) {
      setToken(newToken);
      localStorage.setItem("token", newToken);
    }
  };

  const login = async (formData) => {
    try {
      const response = await fetch(`${baseUrl}/auth/token`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        refreshToken(data.access_token);
        return { success: true };
      } else {
        if (response.status === 403 && data.detail === "Email not verified") {
          return {
            success: false,
            message: `Email not verified. A verification email has been sent to ${data.email}.`,
            status: 403,
          };
        }
        return { success: false, message: data.detail, status: response.status };
      }
    } catch (error) {
      return { success: false, message: "Login failed", status: 500 };
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUserInfo(null);
    hasFetched.current = false;
    navigate("/");
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        userInfo,
        login,
        logout,
        refreshToken,
        updateUserInfo,
        baseUrl,
        setToken,
        fetchUserInfo,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
