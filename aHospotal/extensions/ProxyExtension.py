# -*- coding: utf-8 -*-

from scrapy import signals


class ProxyExtension(object):

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls()

        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.response_received, signal=signals.response_received)
        return ext

    def spider_opened(spider):
        print (u"自定义拓展代理")

    def response_received(response, request, spider):
        pass
