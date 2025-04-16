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
      const response = await axios.post(`http://127.0.0.1:8000${endpoint}`, {
        username,
        password,
      });

      if (isLogin) {
        setSessionToken(response.data.session_token);
      } else {
        alert("User registered successfully! Please login.");
        setIsLogin(true);
      }
    } catch (error) {
      alert(error.response?.data?.detail || "Something went wrong.");
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>{isLogin ? "Login" : "Register"}</h2>
        <form onSubmit={handleSubmit} style={styles.form}>
          <input
            style={styles.input}
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            style={styles.input}
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit" style={styles.primaryBtn}>
            {isLogin ? "Login" : "Register"}
          </button>
        </form>
        <button style={styles.toggleBtn} onClick={() => setIsLogin(!isLogin)}>
          {isLogin ? "Create an account" : "Back to login"}
        </button>
      </div>
    </div>
  );
};

const styles = {
  container: {
    height: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "#f5f5f5",
  },
  card: {
    padding: "30px",
    width: "300px",
    background: "#fff",
    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
    borderRadius: "10px",
    textAlign: "center",
  },
  title: {
    marginBottom: "20px",
    color: "#333",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "10px",
  },
  input: {
    padding: "10px",
    fontSize: "14px",
    border: "1px solid #ccc",
    borderRadius: "5px",
  },
  primaryBtn: {
    padding: "10px",
    background: "#4CAF50",
    color: "white",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
  },
  toggleBtn: {
    marginTop: "10px",
    padding: "8px",
    background: "transparent",
    color: "#4CAF50",
    border: "none",
    cursor: "pointer",
    textDecoration: "underline",
  },
};

export default Auth;
