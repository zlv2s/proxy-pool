import pymongo
import logging
import os
from pymongo.errors import DuplicateKeyError
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class MongoDB(object):
    def __init__(self):
        self.client = pymongo.MongoClient(os.environ.get("MONGO_DB_URI"))
        self.db = self.client[os.environ.get("DB_NAME")]
        self.proxies = self.db['proxies']
        self.proxies.ensure_index('proxy', unique=True)

    def insert(self, proxy):
        try:
            self.proxies.insert(proxy)
            logging.info(f'插入成功： {proxy}')
        except DuplicateKeyError:
            pass

    def delete(self, conditions):
        self.proxies.remove(conditions)
        logging.info(f'删除成功： {conditions}')

    def update(self, conditions, values):
        self.proxies.update(conditions, {"$set": values})
        logging.info(f'更新成功： {conditions},{values}')

    def get(self, count, conditions=None):
        conditions = conditions if conditions else {}
        count = int(count)
        items = self.proxies.find(conditions)
        # items = self.proxies.find(conditions, limit=count).sort('delay', pymongo.ASCENDING)
        items = list(items)
        return items

    def get_count(self):
        return self.proxies.count({})


if __name__ == '__main__':
    m = MongoDB()
    print(m.get(3))
