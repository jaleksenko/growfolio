// frontend/src/context/AuthConsumerWrapper.jsx
import React, { useContext } from "react";
import { AuthContext } from "./AuthContext";
import { WatchlistProvider } from "./WatchlistContext";
import { PortfolioProvider } from "./PortfolioContext";
import Routes from "../router/Routes.jsx";

const AuthConsumerWrapper = () => {
  const { token } = useContext(AuthContext);

  // Show routes without portfolio if user is not authenticated
  if (!token) {
    return (
      <WatchlistProvider>
        <div className="app">
          <Routes />
        </div>
      </WatchlistProvider>
    );
  }

  // Show routes with portfolio once token is present
  return (
    <WatchlistProvider>
      <PortfolioProvider>
        <div className="app">
          <Routes />
        </div>
      </PortfolioProvider>
    </WatchlistProvider>
  );
};

export default AuthConsumerWrapper;
