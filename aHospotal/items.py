# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import Join


class I36krsContact(scrapy.Item):
    url = scrapy.Field(output_processor=Join())
    title = scrapy.Field(output_processor=Join())
    content = scrapy.Field(output_processor=Join())
    pass


class ProxyIps(scrapy.Item):
    ip = scrapy.Field(output_processor=Join())
    port = scrapy.Field(output_processor=Join())
    # print(ip + ":" + port)


class AhospotalItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class HerbMedicine(scrapy.Item):
    url = scrapy.Field(output_processor=Join())
    name = scrapy.Field(output_processor=Join())
    chinese_spell = scrapy.Field(output_processor=Join())
    img = scrapy.Field(output_processor=Join())
    alias = scrapy.Field(output_processor=Join())
    effect = scrapy.Field(output_processor=Join())
    english = scrapy.Field(output_processor=Join())
    origin = scrapy.Field(output_processor=Join())
    poison = scrapy.Field(output_processor=Join())
    channel = scrapy.Field(output_processor=Join())
    property = scrapy.Field(output_processor=Join())
    flavor = scrapy.Field(output_processor=Join())
    content = scrapy.Field(output_processor=Join())

    pass


class AirbubIdx(scrapy.Item):
    id = scrapy.Field(output_processor=Join())
    link = scrapy.Field(output_processor=Join())
    label1 = scrapy.Field(output_processor=Join())
    title = scrapy.Field(output_processor=Join())
    price = scrapy.Field(output_processor=Join())


class Airbnb_Location(scrapy.Item):
    id = scrapy.Field(output_processor=Join())
    location = scrapy.Field(output_processor=Join())
    location2 = scrapy.Field(output_processor=Join())


class Airbnb_Calendar(scrapy.Item):
    id = scrapy.Field(output_processor=Join())
    json = scrapy.Field()

