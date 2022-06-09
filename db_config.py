import redis
import os
from dotenv import load_dotenv

load_dotenv()
redis_host = os.getenv('REDIS_HOST')
redis_port = os.getenv('REDIS_PORT')
redis_password = os.getenv('REDIS_PASSWORD')


FRODE_DB = redis.StrictRedis(
    host=redis_host,
    port=redis_port,
    db=0,
    password=redis_password,
    charset="utf-8",
    decode_responses=True
)
