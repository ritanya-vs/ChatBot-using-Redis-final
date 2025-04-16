import redis
import os

REDIS_HOST = "redis-11733.c15.us-east-1-2.ec2.redns.redis-cloud.com"
REDIS_PORT = 11733
REDIS_PASSWORD = "lalritsamhar"

# Create a persistent Redis connection
redis_client = None

def get_redis_connection():
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True,
            socket_timeout=5  # Prevents hanging connections
        )
    return redis_client