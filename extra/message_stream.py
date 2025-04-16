import redis
import time
from redis_handler import get_redis_client

REDIS_STREAM_NAME = "chat_stream"

redis_client = get_redis_client()

# ✅ Function to send a message
def send_message(user, message):
    redis_client.xadd(REDIS_STREAM_NAME, {"user": user, "message": message}, maxlen=1000)
    print(f"📩 Message sent: {user} -> {message}")

# ✅ Function to listen for messages
def listen_for_messages(last_id="$"):
    print("👂 Listening for new messages...")
    while True:
        try:
            # Block for 5 seconds & check for new messages
            response = redis_client.xread({REDIS_STREAM_NAME: last_id}, block=5000)
            if response:
                stream, messages = response[0]
                for msg_id, msg in messages:
                    print(f"💬 {msg['user']}: {msg['message']}")
                    last_id = msg_id  # Update last read ID
        except Exception as e:
            print("❌ Error in listener:", e)
            time.sleep(2)

# ✅ Test sending & listening
if __name__ == "__main__":
    import threading

    # Start listener in a separate thread
    threading.Thread(target=listen_for_messages, daemon=True).start()

    # Send test messages
    while True:
        user = input("Enter your name: ")
        message = input("Enter message: ")
        send_message(user, message)
