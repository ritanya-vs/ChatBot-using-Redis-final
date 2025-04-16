import redis
from redis_handler import get_redis_client

REDIS_ONLINE_USERS = "online_users"

redis_client = get_redis_client()

# ✅ Mark user as online
def user_online(username):
    redis_client.sadd(REDIS_ONLINE_USERS, username)
    print(f"🟢 {username} is online")

# ✅ Mark user as offline
def user_offline(username):
    redis_client.srem(REDIS_ONLINE_USERS, username)
    print(f"🔴 {username} is offline")

# ✅ Get all online users
def get_online_users():
    return redis_client.smembers(REDIS_ONLINE_USERS)

# ✅ Test functionality
if __name__ == "__main__":
    while True:
        action = input("\n1. Login\n2. Logout\n3. Show Online Users\nChoice: ")
        if action == "1":
            user = input("Enter your name: ")
            user_online(user)
        elif action == "2":
            user = input("Enter your name: ")
            user_offline(user)
        elif action == "3":
            print("👥 Online Users:", get_online_users())
