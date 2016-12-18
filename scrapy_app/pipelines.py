from collections import OrderedDict
import logging
from scrapy import signals

from pymongo import MongoClient
from scrapy_app.settings import MONGODB_SERVER, MONGODB_PORT

class Format(object):
    def process_item(self, item, spider):
        item['website'] = spider.name

        for key, value in item.items():
            item[key] = ' '.join(value.split()).strip()  # remove multiple spaces, then trim
        item = OrderedDict(sorted(item.items(), key=lambda t: t[0]))

        return item

class MongoDb(object):
    def spider_opened(self, spider):
        self.client = MongoClient(MONGODB_SERVER, MONGODB_PORT)

    def process_item(self, item, spider):
        if len(item['Telephone']) > 2 or len(item['Email']) > 2:
            collection = self.client['contactDetail'][spider.name]
            collection.update({'shop_name': item['shop_name']}, item, upsert=True)
            # collection.insert_one(item)

            return item

    def spider_closed(self, spider):
        self.client.close()

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline


