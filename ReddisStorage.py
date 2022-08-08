import redis
from Include.DataSplitter import DataSplitter

class ReddisDataSaver:
    def __init__(self, abbrBase = redis.StrictRedis(host='localhost', port=6379, charset="utf-8", decode_responses=True, db=1), saveData = DataSplitter()):
        # база данных пар ключ - строка
        self.abbrBase = abbrBase
        self.saveData = saveData
        #print("Create ReddisDataSaver")
        #print("Cleaning redis storage")
        self.abbrBase.flushdb()


    def putPair(self, abbr):
        if not self.abbrBase.exists(hash(abbr)):
            self.abbrBase.append(hash(abbr), abbr)
            self.saveData.fileReader(abbr)
            #print("hash(abbr) = " + str(hash(abbr)) + " " + self.abbrBase.get(hash(abbr)))
        return
"""
    def printReddisStorage(self):
        self.putLog.info("redis storage size is " + str(self.abbrBase.dbsize()))
"""