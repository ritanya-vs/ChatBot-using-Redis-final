import redis

REDIS_HOST = "3.82.222.27"
REDIS_PORT = 11733
REDIS_PASSWORD = "lalritsamhar"

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True
)

try:
    response = redis_client.ping()
    print("✅ PING Response:", response)
except Exception as e:
    print("❌ Connection Failed:", e)
