class WebSocketManager {
  constructor(sessionToken, onMessageReceived) {
    this.sender = sessionToken;
    this.ws = new WebSocket(`ws://127.0.0.1:8000/ws?session_token=${sessionToken}`);

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      onMessageReceived(message);
    };

    this.ws.onclose = () => {
      console.warn("WebSocket closed.");
    };

    this.ws.onerror = (err) => {
      console.error("WebSocket error", err);
    };
  }

  sendMessage(recipient, message) {
    this.ws.send(
      JSON.stringify({
        sender: this.sender,
        recipient,
        message,
      })
    );
  }

  closeConnection() {
    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.close();
    }
  }
}

export default WebSocketManager;
