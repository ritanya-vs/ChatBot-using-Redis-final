from fastapi import WebSocket, HTTPException
from auth import authenticate_user
from redis_client import *
import redis
import asyncio
import json

class WebSocketManager:
    def __init__(self):
        self.active_connections = {}  # Store user_id -> WebSocket mapping
        self.redis_client = get_redis_connection()

    async def connect(self, session_token: str, websocket: WebSocket):
        """Authenticate user and store WebSocket connection."""
        try:
            user_id = authenticate_user(session_token)  # Authenticate user using session_token
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid session token")

            await websocket.accept()  # Accept the WebSocket connection
            self.active_connections[user_id] = websocket  # Add WebSocket to active connections

            # Store user as online in Redis
            self.redis_client.sadd("online_users", user_id)
            
            # Fetch missed messages for this user (if any)
            await self.fetch_missed_messages(user_id, websocket)

        except HTTPException:
            await websocket.close()

    def disconnect(self, user_id: str):
        """Disconnect user and remove from active connections."""
        websocket = self.active_connections.pop(user_id, None)
        if websocket:
            try:
                asyncio.create_task(websocket.close())
            except Exception as e:
                print(f"Error closing WebSocket for {user_id}: {e}")

        # Remove user from Redis online users set
        self.redis_client.srem("online_users", user_id)

    async def send_message(self, sender_id: str, recipient_id: str, message: str):
        """Send message to a recipient and store it in Redis."""
        chat_key = f"chat:{sender_id}:{recipient_id}"  # Unique chat stream

        # Store message in Redis Stream
        message_data = {
            "sender": sender_id,
            "recipient": recipient_id,
            "message": message
        }
        self.redis_client.xadd(chat_key, {"message": json.dumps(message_data)})

        # Send message to recipient if online
        if recipient_id in self.active_connections:
            await self.active_connections[recipient_id].send_text(json.dumps(message_data))

    async def receive_message(self, websocket: WebSocket, sender_id: str):
        """Listen for messages from a sender."""
        while True:
            try:
                data = await websocket.receive_text()  # Receive message as text
                data = json.loads(data)  # Convert string to JSON object

                recipient_id = data.get("recipient")
                message = data.get("message")

                if recipient_id and message:
                    await self.send_message(sender_id, recipient_id, message)

            except Exception as e:
                print(f"Error receiving message: {e}")
                self.disconnect(sender_id)  # Disconnect user on error
                break

    async def fetch_missed_messages(self, user_id: str, websocket: WebSocket):
        """Retrieve unread messages from Redis and send them to the user."""
        keys = self.redis_client.keys(f"chat:*:{user_id}")  # Get all chats for the user

        for chat_key in keys:
            messages = self.redis_client.xrange(chat_key)
            for _, message_data in messages:
                print("Received data:", message_data)
                msg = json.loads(message_data["message"])  # Decode bytes
                await websocket.send_text(json.dumps(msg))  # Send the message to the client
