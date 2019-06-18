# -*- coding: utf-8 -*-
import scrapy
import urllib
from aHospotal.items import HerbMedicine

from scrapy.loader import ItemLoader


class HerbMedicineSpider(scrapy.Spider):
    name = 'herb-medicine'
    # allowed_domains = ['web']
    start_urls = ['http://www.a-hospital.com/w/%E4%B8%AD%E8%8D%AF%E5%9B%BE%E5%85%B8']

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'aHospotal.middlewares.ProxyMiddleware': 1,
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

    def parse_medicine(self, response):
        product = response.css('table.infobox.hproduct')  ##.xpath('tr')
        l = ItemLoader(item=HerbMedicine(), response=response)
        l.add_value('url', response.request.url)
        l.add_value('name', product.xpath('tr[1]/th/span/text()').extract_first())
        l.add_value('chinese_spell', product.xpath('tr[1]/th/span/span/text()').extract_first())
        l.add_value('img', response.urljoin(product.xpath('tr[2]//a/@href').extract_first()))
        l.add_value('alias', product.xpath('tr[3]//td//node()/text()').extract())
        l.add_value('effect', product.xpath('tr[4]//td//node()/text()').extract())
        l.add_value('english', product.xpath('tr[5]//td//node()/text()').extract())
        l.add_value('origin', product.xpath('tr[6]//td//node()/text()').extract())
        l.add_value('poison', product.xpath('tr[7]//td//node()/text()').extract())
        l.add_value('channel', product.xpath('tr[8]//td//node()/text()').extract())
        l.add_value('property', product.xpath('tr[9]//td//node()/text()').extract())
        l.add_value('flavor', product.xpath('tr[10]//td//node()/text()').extract())
        l.add_value('content', response.xpath('//div[@id="bodyContent"]').xpath(
            'p/text() | h2/text() | p//node()/text() | h2//node()/text()').extract())

        yield l.load_item()

        # response.css('div#bodyContent').xpath('p')

        print(response.url)

    def parse_idx(self, response):
        herb_medicines = response.css('#masonry-container').xpath('table//tr[2]//a')
        for m in herb_medicines:
            url = response.urljoin(m.xpath('@href').extract_first())
            print(','.join(m.xpath('text()').extract()))
            yield scrapy.Request(url, callback=self.parse_medicine)

    def parse(self, response):
        herb_medicines = response.css('#masonry-container').xpath('table//tr[2]//a')
        for m in herb_medicines:
            url = response.urljoin(m.xpath('@href').extract_first())
            print(','.join(m.xpath('text()').extract()))
            yield scrapy.Request(url, callback=self.parse_medicine)
        # pager = response.css('td.navbox-list.navbox-odd.wlist').xpath('div/ul/li/a')
        # # p = pager[0]
        # for p in pager:
        #     url = response.urljoin(p.xpath('@href').extract_first())
        #     print(url)
        #     yield scrapy.Request(url, callback=self.parse_idx)
