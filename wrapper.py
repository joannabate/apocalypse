import datetime
import json
import time
from typing import Callable
import redis
from threading import Thread

def rate_limited(rate: float):
    min_interval = rate

    def decorator(func):
        last_called = [0.0]

        def rate_limited_function(*args, **kwargs):
            elapsed = time.perf_counter() - last_called[0]
            left_to_wait = min_interval - elapsed

            if left_to_wait > 0:
                return

            ret = func(*args, **kwargs)
            last_called[0] = time.perf_counter()
            return ret

        return rate_limited_function

    return decorator

class RedisWrapper:
    def __init__(self, client='', host='192.168.0.102', port=6379, db=0, heartbeat_interval=5):
        self.redis = redis.Redis(host=host, port=port, db=db)
        self.pubsub = self.redis.pubsub()
        self.client_name = client
        self.heartbeat_interval = heartbeat_interval
        self.disconnect_timeout = 3*heartbeat_interval
        self.heartbeat_thread = None
        self.monitor_thread = None
        self.closed = False

        if self.client_name != '':
            self.heartbeat_thread = Thread(target=self._heartbeat).start()
 
    def monitor_clients(self):
        if self.monitor_thread is None:
            self.monitor_thread = Thread(target=self._client_monitor).start()

    def _heartbeat(self):
        while not self.closed:
            self.set('client_'+self.client_name, "connected")
            time.sleep(self.heartbeat_interval)

    def _client_monitor(self):
        while not self.closed:
            time.sleep(self.disconnect_timeout)
            for key in self.redis.keys('client_*'):
                data = self.get(key.decode(), self.disconnect_timeout)
                if data is None:
                    self.set(key.decode(), "disconnected")

    def _get_key_data(self, key):
        raw_data = self.redis.get(key)
        if raw_data is None:
            return None
        if key.startswith('_'):
            return {'value': raw_data.decode(), 'timestamp': datetime.datetime.now().isoformat()}
        ret = json.loads(raw_data)
        if type(ret) is dict:
            return ret
        else:
            print('WARNING: Key is not a dict: '+key)
            return {'value': json.dumps(ret), 'timestamp': datetime.datetime.now().isoformat()}

    def _set_key_data(self, key, data):
        self.redis.set(key, json.dumps(data))

    def close(self):
        if self.client_name != '':
            self.set('client_'+self.client_name, "disconnected")
        self.closed = True
        if self.heartbeat_thread is not None:
            self.heartbeat_thread.join()
        if self.monitor_thread is not None:
            self.monitor_thread.join()
        self.redis.close()

    def set(self, key: str, value: str):
        data = {
            'value': value,
            'timestamp': datetime.datetime.now().isoformat(),
        }
        self._set_key_data(key, data)
        self.redis.publish(key, json.dumps(data))

    # def get(self, key: str, default: str | None = None, max_age_seconds: float | None = None):
    #     data = self._get_key_data(key)
    #     if data is None:
    #         return default
    #     timestamp = datetime.datetime.fromisoformat(data['timestamp'])
    #     if max_age_seconds is not None:
    #         if (datetime.datetime.now() - timestamp).total_seconds() > max_age_seconds:
    #             return default
    #     return data['value']

    # def subscribe(self, key: str, callback : Callable, rate: float | None  = None, call_max_age_seconds: float | None = None):
    #     if call_max_age_seconds is not None:
    #         value = self.get(key, call_max_age_seconds)
    #         if value is not None:
    #             callback(value)
    #     if rate is not None:
    #         callback = rate_limited(rate)(callback)
    #     self.pubsub.subscribe(**{key: lambda message: callback(json.loads(message['data'])['value'])})

    def subscribe_all(self, callback : Callable, call_on_existing: bool = False):
        if call_on_existing:
            for key in self.redis.keys('*'):
                print('sub | '+key.decode())
                data = self._get_key_data(key.decode())
                if data is not None:
                    print('callback on '+key.decode()[:10]+'...')
                    callback(key.decode(), data['value'])
                else:
                    print('no data for '+key.decode())
        self.pubsub.psubscribe(**{'*': lambda message: callback(message['channel'].decode(), json.loads(message['data'])['value'])})

    def run_forever(self):
        for message in self.pubsub.listen():
            pass  # just block to keep script running

    def run_in_thread(self):
        Thread(target=self.run_forever).start()