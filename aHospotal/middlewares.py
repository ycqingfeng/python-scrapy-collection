# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError
from twisted.web.client import ResponseFailed
from scrapy.core.downloader.handlers.http11 import TunnelError

from scrapy import signals
import base64
import random
import redis
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
import pymongo
import aHospotal.settings as SETTING


class AhospotalSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class AhospotalDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ProxyMiddleware(object):
    """ 随机选代理 """

    def __init__(self):
        self.output = open('data', 'w')
        self.redisClient = redis.Redis(host='localhost', port=6379, password='password', db=1)

        self.PROXIES = [
            {'ip_port': "180.168.13.26:8000", 'user_pass': None},
            {'ip_port': "101.81.217.191:8060", 'user_pass': None},
            {'ip_port': "180.175.3.0:8060", 'user_pass': None},
            {'ip_port': "101.132.100.26:80", 'user_pass': None},
            {'ip_port': "115.159.31.195:8080", 'user_pass': None},
            {'ip_port': "139.224.15.243:80", 'user_pass': None},
            {'ip_port': "118.25.89.245:8080", 'user_pass': None},
            # {'ip_port': "106.14.176.162:80"   , 'user_pass': None},
            {'ip_port': "139.196.22.147:80", 'user_pass': None},
        ]
        # client = pymongo.MongoClient(SETTING.MONGO_URI)
        # db = client[SETTING.MONGO_DATABASE]
        # ips = db['ips'].find()
        # for ip in ips:
        #     self.PROXIES.append({'ip_port': '%(ip)s:%(port)s' % ip, 'user_pass': ''})

    def process_request(self, request, spider):
        proxy = random.choice(self.PROXIES)
        # if proxy['user_pass'] is not None:
        #     request.meta['proxy'] = "http://%s" % proxy['ip_port']
        #     encoded_user_pass = base64.encodestring(proxy['user_pass'])
        #     request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass
        #     print("**************ProxyMiddleware have pass************" + proxy['ip_port'])
        # else:
        print("ProxyMiddleware no pass" + proxy['ip_port'] + " --> " + request.url)
        request.meta['proxy'] = "http://%s" % proxy['ip_port']

    def process_response(self, request, response, spider):
        if response.status in (200,):
            return response
        elif response.status in (404, 403, 302):
            print ("XXXXXXXX proxy detected: " + request.meta['proxy'] + "--->response:" + str(
                response.status))

            error_count = self.redisClient.incr(request.url, amount=1)
            if error_count < 10:
                req = request.copy()
                return req
            else:
                self.output.write(request.url + '\r\n')

    def process_exception(self, request, exception, spider):
        pass
        print ("================================"
               "request " + request.url + "    "
                                          "proxy detected: " + request.meta['proxy'])
        return request.copy()


class CustomerUserAgentMiddleware(UserAgentMiddleware):
    """ 自定义设置UserAgent """

    def __init__(self, user_agent):
        self.user_agent = user_agent

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            user_agent=crawler.settings.get('USER_AGENTS')
        )

    def process_request(self, request, spider):
        agent = random.choice(self.user_agent)
        request.headers['User-Agent'] = agent
