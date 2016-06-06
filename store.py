import redis
import config

pool = redis.ConnectionPool(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
r = redis.StrictRedis(connection_pool=pool)
