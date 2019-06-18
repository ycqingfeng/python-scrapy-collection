# -*- coding: utf-8 -*-
import json
from json import JSONEncoder

import scrapy
from scrapy.loader import ItemLoader
from aHospotal.items import I36krsContact
from urllib import urlencode


class A36krSpider(scrapy.Spider):
    name = '36kr'
    # allowed_domains = ['web']
    # start_urls = ['https://www.36kr.com/information/contact']
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            # 'aHospotal.middlewares.ProxyMiddleware': 1,
            'aHospotal.middlewares.CustomerUserAgentMiddleware': 400,
        },
        'EXTENSIONS': {
            'aHospotal.extensions.ProxyExtension.ProxyExtension': 100
        },
        # 'RETRY_ENABLED': True,
        'DOWNLOAD_DELAY': 0.5,
        'REDIRECT_ENABLED': False,
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter'
    }
    handle_httpstatus_list = [302]

    def start_requests(self):
        params = {'type': 'web', 'feed_id': '305'}
        return [scrapy.Request(url='https://36kr.com/pp/api/feed-stream?' + urlencode(params),
                               method='GET',
                               callback=self.onResponse)]

    def onResponse(self, response):
        body = json.loads(response.body)
        last_id = None
        if body['code'] == 0:
            items = body['data']['items'];
            for _item in items:
                # l = ItemLoader(item=I36krsContact(), response=response)
                # l.add_value("url", _item['id'])
                # l.add_value("title", _item['title'])
                # yield l.load_item()
                last_id = _item['entity_id']
                url = response.urljoin("https://www.36kr.com/p/" + ((str)(_item['entity_id'])))
                yield scrapy.Request(url, callback=self.parse_detail)

        if last_id is not None:
            params = {'type': 'web', 'feed_id': '305', 'b_id': last_id, 'per_page': 30}
            yield [scrapy.Request(url='https://36kr.com/pp/api/feed-stream?' + urlencode(params),
                                  method='GET',
                                  callback=self.onResponse)]

    def parse_detail(self, response):
        url = response.request.url
        title = response.xpath('//title').extract()
        content = response.xpath('//div[contains(@class,"article-wrapper")]//*/text()').extract()

        l = ItemLoader(item=I36krsContact(), response=response)
        l.add_value("url", url)
        l.add_value("title", title)
        l.add_value("content", content)
        yield l.load_item()

        # def parse(self, response):
        #     lis = response.css('.information-flow-item .article-item-title')
        #     for _lis in lis:
        #         l = ItemLoader(item=I36krsContact(), response=response)
        #         l.add_value("url", _lis.xpath("@href").extract())
        #         l.add_value("title", _lis.xpath('text()').extract())
        #         yield l.load_item()
        #
        #         url = response.urljoin(_lis.xpath('@href').extract_first())
        #         yield scrapy.Request(url, callback=self.parse_medicine)
