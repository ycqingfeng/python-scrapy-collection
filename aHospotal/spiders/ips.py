# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from aHospotal.items import ProxyIps


class IpsSpider(scrapy.Spider):
    name = 'ips'
    # allowed_domains = ['https://www.xicidaili.com/wt/']
    start_urls = ['https://www.xicidaili.com/wt/']
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'aHospotal.middlewares.CustomerUserAgentMiddleware': 749,
        },
        'EXTENSIONS': {
            'aHospotal.extensions.ProxyExtension.ProxyExtension': 100
        }
    }

    def parse(self, response):
        trs = response.css('table#ip_list tr')
        for tr in trs:
            l = ItemLoader(item=ProxyIps(), response=response)
            l.add_value("ip", tr.xpath('td[2]/text()').extract_first())
            l.add_value("port", tr.xpath('td[3]/text()').extract_first())
            yield l.load_item()

        next_url = response.css('.next_page').xpath('@href').extract_first()
        if next_url is not None:
            next_url = response.urljoin(next_url)
            yield scrapy.Request(next_url, callback=self.parse)
