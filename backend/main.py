from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends,Query,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from websocket_manager import WebSocketManager
from auth import authenticate_user
from auth import router as auth_router
from dotenv import load_dotenv
from redis_client import get_redis_connection
from datetime import datetime,timezone,timedelta

import os

# Load environment variables
load_dotenv(dotenv_path=".env")

# Initialize FastAPI app
app = FastAPI(title="Redis-Powered Chat App", docs_url="/docs")

# Include authentication routes
app.include_router(auth_router, prefix="/auth")

# Initialize WebSocket manager
manager = WebSocketManager()

# Enable CORS (for frontend communication)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change for security)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connection for messaging."""
    
    # Extract session_token from query params
    session_token = websocket.query_params.get("session_token")
    print(f"Received WebSocket request with session_token: {session_token}")  # Debugging
    
    # Validate user authentication and connect
    user_id = authenticate_user(session_token)
    if not user_id:
        await websocket.close()  # Close connection if authentication fails
        return

    # Connect user and manage the WebSocket session
    await manager.connect(session_token, websocket)
    
    try:
        await manager.receive_message(websocket, user_id)  # Start receiving messages for this user
    except WebSocketDisconnect:
        print(f"User {user_id} disconnected.")  # Handle user disconnect
    except Exception as e:
        print(f"Error: {e}")  # Handle any unexpected errors
    finally:
        await manager.disconnect(user_id)  
 
@app.get("/status/{username}")
def get_user_status(username: str):
    redis_client = get_redis_connection()
    online = redis_client.sismember("online_users", username)
    last_seen = redis_client.hget("user:last_seen", username)
    if (last_seen):
        dt_utc = datetime.fromisoformat(last_seen)
        ist = timezone(timedelta(hours=5, minutes=30))
        dt_ist = dt_utc.astimezone(ist)
        formatted_time = dt_ist.strftime("%B %d, %Y %I:%M %p")
    else:
        formatted_time = ""
    return {
        "username": username,
        "online": bool(online),
        "last_seen": formatted_time
    }    
       

# Redis Ping Test
@app.get("/ping_redis")
async def ping_redis():
    try:
        redis_info = {
            "REDIS_HOST": os.getenv("REDIS_HOST"),
            "REDIS_PORT": os.getenv("REDIS_PORT"),
            "REDIS_PASSWORD": os.getenv("REDIS_PASSWORD")[:4] + "*"
        }

        redis_client = get_redis_connection()
        redis_client.set("test_key", "Hello, Redis!")
        value = redis_client.get("test_key")

        return {
            "message": "Redis is working!",
            "value": value.decode("utf-8") if value else None,
            "redis_info": redis_info
        }
    except Exception as e:
        return {
            "error": str(e),
            "redis_info": redis_info
        }
        

# Endpoint to Check Environment Variables
@app.get("/env_test")
async def env_test():
    return {
        "REDIS_HOST": os.getenv("REDIS_HOST"),
        "REDIS_PORT": os.getenv("REDIS_PORT"),
        "REDIS_PASSWORD": os.getenv("REDIS_PASSWORD")[:4] + "*"
    }
    

# Home Route
@app.get("/")
def home():
    return {"message": "Welcome to the Redis-Powered Chat App!"}
