import redis
import pickle
from functools import lru_cache
class Datastore():
    def __init__(self):
        self.now_playing = None
        self.r = redis.Redis()

    def getSavedDevice(self, id):
        return self._getSavedItem("device:"+id)

    def _getSavedItem(self, id):
        pickled_device = self.r.get(id)
        return pickle.loads(pickled_device)

    def getAllSavedDevices(self):
        return list(map(lambda idx: self._getSavedItem(idx), self.r.keys("device:*")))

    def getDevices(self):
        return list(map(lambda idx: self._getSavedItem(idx), self.r.keys("show-uri:*")))

    def clearDevices(self):
        devices = self.r.keys("device:*")
        if (len(devices) == 0):
            return
        self.r.delete(*devices)

    def clear(self):
        self.r.flushdb()