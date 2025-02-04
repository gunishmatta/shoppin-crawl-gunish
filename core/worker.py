import os

from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

redis_url = (
    f'redis://{f":{REDIS_PASSWORD}@" if REDIS_PASSWORD else ""}'
    f'{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
)

redis_broker = ListQueueBroker(
    url=redis_url
).with_result_backend(RedisAsyncResultBackend(redis_url))
