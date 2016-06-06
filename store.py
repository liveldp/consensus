import redis
import config

pool = redis.ConnectionPool(host=config.DATA_HOST, port=config.DATA_PORT, db=config.DATA_DB)
r = redis.StrictRedis(connection_pool=pool)
