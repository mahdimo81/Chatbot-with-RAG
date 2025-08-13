import React from "react";
import "../styles/App.css";
import Login from "./Login";
import Signup from "./Signup";
import Error from "./Error";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

function Auth() {
  return (
    <div className="App">
      <Router>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="*" element={<Error />} />
        </Routes>
      </Router>
    </div>
  );
}

export default Auth;
