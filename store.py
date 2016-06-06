import redis

pool = redis.ConnectionPool(host='localhost', port=6379, db=2)
r = redis.StrictRedis(connection_pool=pool)
