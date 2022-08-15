import redis
from config import REDIS_URL, NUMBER_STORAGE_SESSION

session_storage = redis.from_url(
    REDIS_URL, db=NUMBER_STORAGE_SESSION, decode_responses=False)
