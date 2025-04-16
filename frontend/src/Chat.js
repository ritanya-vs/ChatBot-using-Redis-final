import React, { useState, useEffect, useRef } from "react";
import WebSocketManager from "./WebSocketManager";

const Chat = ({ sessionToken }) => {
  const [messagesByContact, setMessagesByContact] = useState({});
  const [contacts, setContacts] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [message, setMessage] = useState("");
  const [unreadCounts, setUnreadCounts] = useState({});
  const wsManagerRef = useRef(null);
  const [username, setUsername] = useState("");
  const [contactStatuses, setContactStatuses] = useState({});


  useEffect(() => {
    const fetchUsername = async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/auth/whoami?session_token=${sessionToken}`
        );
        const data = await response.json();
        setUsername(data.username);
      } catch (err) {
        console.error("Failed to fetch username", err);
      }
    };
  
    if (sessionToken) {
      fetchUsername();
    }
  }, [sessionToken]);

  // 1️⃣ useEffect to fetch username
useEffect(() => {
  // fetchUsername logic
}, [sessionToken]);

// 2️⃣ useEffect to setup WebSocketManager
useEffect(() => {
  // WebSocketManager logic
}, [sessionToken]);

// 3️⃣ 🔄 NEW useEffect to auto-refresh user statuses
useEffect(() => {
  const fetchStatuses = async () => {
    const updatedStatuses = {};

    for (const contact of contacts) {
      try {
        const res = await fetch(`http://localhost:8000/status/${contact}`);
        const data = await res.json();
        updatedStatuses[contact] = data;
      } catch (err) {
        console.error(`Error fetching status for ${contact}`, err);
      }
    }

    setContactStatuses(updatedStatuses);
  };

  if (contacts.length > 0) {
    fetchStatuses();
  }

  const interval = setInterval(fetchStatuses, 5000);
  return () => clearInterval(interval);
}, [contacts]);

  

  useEffect(() => {
    wsManagerRef.current = new WebSocketManager(sessionToken, (msg) => {
      const contact = msg.sender === sessionToken ? msg.recipient : msg.sender;

      setMessagesByContact((prev) => ({
        ...prev,
        [contact]: [...(prev[contact] || []), msg],
      }));

      setContacts((prev) => {
        const newContacts = new Set(prev);
        newContacts.add(contact);
        return Array.from(newContacts);
      });

      if (contact !== activeChat && msg.sender !== sessionToken) {
        setUnreadCounts((prev) => ({
          ...prev,
          [contact]: (prev[contact] || 0) + 1,
        }));
      }
    });

    return () => {
      wsManagerRef.current?.closeConnection();
    };
  }, [sessionToken]);

  const sendMessage = () => {
    if (wsManagerRef.current && message && activeChat) {
      const msg = {
        sender: sessionToken,
        recipient: activeChat,
        message,
      };

      wsManagerRef.current.sendMessage(activeChat, message);

      const contact = msg.sender === sessionToken ? msg.recipient : msg.sender;

      setMessagesByContact((prev) => ({
        ...prev,
        [contact]: [...(prev[contact] || []), msg],
      }));

      setMessage("");
    }
  };

  const openChat = (contact) => {
    setActiveChat(contact);
    setUnreadCounts((prev) => ({ ...prev, [contact]: 0 }));
  };

  const filteredMessages = activeChat ? messagesByContact[activeChat] || [] : [];

  return (
    <div style={styles.container}>
      <div style={styles.sidebar}>
      <h3 style={{ marginBottom: "10px" }}>👤 {username ? `Logged in as ${username}` : "Loading..."}</h3>
      {contacts.map((contact) => {
        const status = contactStatuses[contact];

        return (
          <div
            key={contact}
            onClick={() => openChat(contact)}
            style={{
              ...styles.contact,
              backgroundColor:
                contact === activeChat ? "#d1f0c1" : "transparent",
            }}
          >
            <div style={{ fontWeight: "bold" }}>{contact}</div>
            <div style={{ fontSize: "12px", color: "gray" }}>
              {status?.online
                ? "Online"
                : status?.last_seen
                ? `Last seen: ${status.last_seen}`
                : "Loading..."}
            </div>

            {unreadCounts[contact] > 0 && (
              <span style={styles.unread}>{unreadCounts[contact]}</span>
            )}
          </div>
        );
      })}

      </div>

      <div style={styles.chatSection}>
        {activeChat ? (
          <>
            <div style={styles.chatHeader}>Chat with {activeChat}</div>
            <div style={styles.messages}>
              {filteredMessages.map((msg, idx) => (
                <div
                  key={idx}
                  style={{
                    ...styles.message,
                    alignSelf:
                      msg.sender === sessionToken ? "flex-end" : "flex-start",
                    backgroundColor:
                      msg.sender === sessionToken ? "#dcf8c6" : "#fff",
                  }}
                >
                  {msg.message}
                </div>
              ))}
            </div>

            <div style={styles.inputContainer}>
              <input
                style={styles.input}
                type="text"
                placeholder="Type a message..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
              />
              <button style={styles.button} onClick={sendMessage}>
                Send
              </button>
            </div>
          </>
        ) : (
          <div style={styles.placeholder}>Select a chat to start messaging</div>
        )}
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: "flex",
    height: "100vh",
    fontFamily: "Arial, sans-serif",
  },
  sidebar: {
    width: "250px",
    borderRight: "1px solid #ccc",
    padding: "10px",
    overflowY: "auto",
  },
  contact: {
    padding: "10px",
    borderBottom: "1px solid #eee",
    cursor: "pointer",
    position: "relative",
  },
  unread: {
    backgroundColor: "red",
    color: "white",
    borderRadius: "50%",
    padding: "2px 6px",
    fontSize: "12px",
    position: "absolute",
    top: "10px",
    right: "10px",
  },
  chatSection: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
  },
  chatHeader: {
    padding: "10px",
    borderBottom: "1px solid #ccc",
    backgroundColor: "#f0f0f0",
    fontWeight: "bold",
  },
  messages: {
    flex: 1,
    padding: "10px",
    overflowY: "auto",
    display: "flex",
    flexDirection: "column",
    gap: "8px",
  },
  message: {
    maxWidth: "60%",
    padding: "10px",
    borderRadius: "10px",
  },
  inputContainer: {
    display: "flex",
    padding: "10px",
    borderTop: "1px solid #ccc",
  },
  input: {
    flex: 1,
    padding: "10px",
    fontSize: "14px",
    border: "1px solid #ccc",
    borderRadius: "5px",
    marginRight: "10px",
  },
  button: {
    padding: "10px 20px",
    cursor: "pointer",
  },
  placeholder: {
    flex: 1,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "18px",
    color: "#999",
  },
};

export default Chat;
