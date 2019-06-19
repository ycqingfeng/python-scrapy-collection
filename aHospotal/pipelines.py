# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import aHospotal.items as items
import urllib2
import re
import json
import datetime


class AhospotalPipeline(object):
    collection_name = 'aHospital'
    collection_ips = 'ips'
    collection_36krs = "36krs"
    collection_airbnb = "airbnb"

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        spider.db = self.db

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, items.I36krsContact):
            self.db[self.collection_36krs].insert_one(dict(item))
        if isinstance(item, items.HerbMedicine):
            self.db[self.collection_name].insert_one(dict(item))

        # 爱彼迎
        if isinstance(item, items.AirbubIdx):
            self.process_airbnb_idx(item)
        if isinstance(item, items.Airbnb_Location):
            self.process_airbnb_location(item)
        if isinstance(item, items.Airbnb_Calendar):
            self.process_airbnb_calendar(item)
        return item

    def process_airbnb_calendar(self, item):
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        day_after_tomorrow = (datetime.datetime.now() + datetime.timedelta(days=2)).strftime('%Y-%m-%d')

        item_id = item.get('id')
        json_str = item.get('json')
        json_obj = json.loads(json_str[0])
        _calendar_months = json_obj['calendar_months']

        dict = {}
        dict['date'] = today
        for month in _calendar_months:
            for day in month['days']:
                if day['date'] == tomorrow:
                    dict['offset01'] = {
                        'checkin': day['available_for_checkin'],
                        'price': day['price']
                    }
                elif day['date'] == day_after_tomorrow:
                    dict['offset02'] = {
                        'checkin': day['available_for_checkin'],
                        'price': day['price']
                    }

        self.db[self.collection_airbnb].update({
            '$and': [
                {"id": item_id},
                {'$nor': [
                    {'calendar': {'$elemMatch': {'date': today}}}
                ]}
            ]
        }, {'$push': {'calendar': dict}})

    def process_airbnb_location(self, item):
        item_id = item.get('id')
        entity = dict(item)
        del entity['id']
        self.db[self.collection_airbnb].update({"id": item_id}, {'$set': entity})

    def process_airbnb_idx(self, item):
        entity = dict(item)
        self.db[self.collection_airbnb].insert_one(entity)
