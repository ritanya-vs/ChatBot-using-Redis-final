import React, { useState } from "react";
import axios from "axios";

const Auth = ({ setSessionToken }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLogin, setIsLogin] = useState(true);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const endpoint = isLogin ? "/auth/login" : "/auth/register";
    
    try {
      const response = await axios.post(`http://127.0.0.1:8000${endpoint}`, { username, password });
      
      if (isLogin) {
        setSessionToken(response.data.session_token);
      } else {
        alert("User registered successfully! Please login.");
        setIsLogin(true);
      }
    } catch (error) {
      alert(error.response.data.detail);
    }
  };

  return (
    <div>
      <h2>{isLogin ? "Login" : "Register"}</h2>
      <form onSubmit={handleSubmit}>
        <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} required />
        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        <button type="submit">{isLogin ? "Login" : "Register"}</button>
      </form>
      <button onClick={() => setIsLogin(!isLogin)}>
        {isLogin ? "Create an account" : "Back to login"}
      </button>
    </div>
  );
};

export default Auth;
