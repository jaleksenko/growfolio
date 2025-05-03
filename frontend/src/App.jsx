// frontend/src/App.jsx
// frontend/src/App.jsx
import React from "react";
import { BrowserRouter } from "react-router-dom";

import { AuthProvider } from "./context/AuthContext";
import AuthConsumerWrapper from "./context/AuthConsumerWrapper";

import "./styles/main.scss";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AuthConsumerWrapper />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;

