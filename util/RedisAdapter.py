from typing import Dict, Any, Union

import redis

import config
from util import pack

class RedisAdapter(object):
    """Creates and maintains a connection to the redis database"""
    def __init__(self, database):
        redis_address = config.REDIS.split(":")
        redis_host = redis_address[0]
        if len(redis_address) > 0:
            redis_port = redis_address[1]
        else:
            redis_port = 6379
        self.db = redis.StrictRedis(host=redis_host, port=redis_port, db=0, password=config.REDIS_PASSWORD)
        database = config.APP_ID + "_" + config.ENVIRONMENT + "_" + str(database)
        self.databases_key = "_dbs"
        self.db.sadd(self.databases_key, database)

        self.mgmt_prefix = database + "_m_"
        self.var_prefix = database + "_v_"

        self.lock_key = self.mgmt_prefix + "locks"
        self.keylist_key = self.mgmt_prefix + "keys"

        self.keylock = self.db.lock(self.keylist_key + "_lock")

    def set(self, key, value):
        self.keylock.acquire()
        try:
            self.db.sadd(self.keylist_key, str(key))
            self.db.set(self.var_prefix + str(key), pack.dumps(value))
        finally:
            self.keylock.release()

    def expire(self, key, seconds):
        self.db.expireat(self.var_prefix + str(key), seconds)
        # Cannot provide key exist queries for expiring keys at the moment
        self.db.srem(self.keylist_key, str(key))

    def get(self, key) -> Union[Dict[Any, Any], None]:
        raw_val = self.db.get(self.var_prefix + str(key))
        if raw_val is not None:
            return pack.loads(raw_val)
        else:
            return None

    def unset(self, key):
        self.keylock.acquire()
        try:
            self.db.srem(self.keylist_key, str(key))
            self.db.delete(self.var_prefix + str(key))
        finally:
            self.keylock.release()

    def exists(self, key):
        return self.db.sismember(self.keylist_key, str(key))

    def list(self) -> Dict[str, Dict[Any, Any]]:
        keys = [key[len(self.var_prefix):] for key in [k.decode("ascii") for k in self.db.keys(self.var_prefix + "*")]]

        return {
            key: self.get(key) for key in keys
        }
