import redis

# 🔴 Replace with your Redis Cloud details
REDIS_HOST = "3.82.222.27"
REDIS_PORT = 11733
REDIS_PASSWORD = "lalritsamhar"

# ✅ Create Redis connection
def get_redis_client():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True
    )

# ✅ Test connection
if __name__ == "__main__":
    try:
        client = get_redis_client()
        print("✅ Connected to Redis Cloud:", client.ping())
    except Exception as e:
        print("❌ Redis Connection Failed:", e)
