from redis_client import get_redis_connection
import json

r = get_redis_connection()

sender_id = "Samridhaa"
recipient_id = "Ritanya"
chat_key = f"chat:{sender_id}:{recipient_id}"

messages = r.xrange(chat_key)

print(f"Missed messages from {sender_id} to {recipient_id}:\n")
for msg_id, msg_data in messages:
    data = json.loads(msg_data['message'])
    print(f"[{msg_id}] {data['sender']} ➡ {data['recipient']}: {data['message']}")
