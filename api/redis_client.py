import time
import redis
from settings import REDIS_URL


def get_redis() -> redis.Redis:
    pool = redis.ConnectionPool.from_url(REDIS_URL)
    return redis.Redis(connection_pool=pool)


REDIS_CLIENT = get_redis()


class RedisModel:
    REDIS_USERS_KEY = 'user_containers'
    REDIS_LOG_KEY = 'user_log_{}'

    REDIS_USER_DATA_KEY = 'user_data_{}'
    REDIS_USER_DATA_MAPPING = {
        'container': 'container',
        'time_start': 'time_start',
        'available_time': 'available_time',
    }

    def get_user_ids(self):
        return REDIS_CLIENT.hkeys(self.REDIS_USERS_KEY)

    def set_user_available_time(self, user_id: int, available_time: float):
        REDIS_CLIENT.hset(
            self.REDIS_USER_DATA_KEY.format(user_id),
            self.REDIS_USER_DATA_MAPPING['available_time'],
            str(available_time)
        )

    def set_user_new_available_time(self, user_id):
        available_time = REDIS_CLIENT.hget(
            self.REDIS_USER_DATA_KEY,
            self.REDIS_USER_DATA_MAPPING['available_time']
        )
        time_start = REDIS_CLIENT.hget(
            self.REDIS_USER_DATA_KEY,
            self.REDIS_USER_DATA_MAPPING['time_start']
        )
        try:
            new_time = float(available_time) - (time.time() - float(time_start))
        except TypeError:
            # Если одного из значений, то выводим значение по умолчанию
            new_time = 1000
        self.set_user_available_time(user_id, new_time)

    def set_container_info(self, user_id: int, container_id):
        REDIS_CLIENT.hset(
            self.REDIS_USER_DATA_KEY.format(user_id),
            self.REDIS_USER_DATA_MAPPING['container'],
            container_id
        )
        REDIS_CLIENT.hset(
            self.REDIS_USER_DATA_KEY.format(user_id),
            self.REDIS_USER_DATA_MAPPING['time_start'],
            time.ctime()
        )
        REDIS_CLIENT.hset(self.REDIS_USERS_KEY, str(user_id), container_id)

    def get_container_id_by_user(self, user_id: int):
        val = REDIS_CLIENT.hget(
            self.REDIS_USER_DATA_KEY.format(user_id),
            self.REDIS_USER_DATA_MAPPING['container']
        )
        if isinstance(val, bytes):
            return val.decode('utf-8')
        return val

    def del_user_container_info(self, user_id):
        REDIS_CLIENT.hdel(
            self.REDIS_USER_DATA_KEY.format(user_id),
            [self.REDIS_USER_DATA_MAPPING['container']]
        )
        REDIS_CLIENT.hdel(self.REDIS_USERS_KEY, [str(user_id)])


redis_model = RedisModel()
