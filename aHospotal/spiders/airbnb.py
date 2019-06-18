# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from aHospotal.items import AirbubIdx, Airbnb_Location, Airbnb_Calendar
import logging
import re
import json
from scrapy.loader.processors import Join


class AirbnbSpider(scrapy.Spider):
    db = None
    url = 'https://www.airbnb.cn/china-guest-moweb-loop/cls_result?items_offset=#{offset}&items_per_grid=10&query=%E6%9D%AD%E5%B7%9E'
    name = 'airbnb'
    start_urls = [
        'https://www.airbnb.cn/china-guest-moweb-loop/cls_result?items_offset=0&items_per_grid=10&query=%E6%9D%AD%E5%B7%9E']
    offset = 20
    calendar_api = "https://www.airbnb.cn/api/v2/calendar_months?_format=with_conditions&count=3&currency=CNY&key=d306zoyjsyarp7ifhu67rjxn52tv0t20&listing_id=${listing_id}&locale=zh&month=5&year=2019"
    logger = logging.getLogger(__name__)
    hit_total = []

    def generate_calendar_api_url(self, listing_id):
        url = self.calendar_api.replace('${listing_id}', listing_id)
        return url

    def parse_calendar_api(self, response):
        item_id = re.findall('\?|&listing_id=(.*?)&', response.url)[1]

        l = ItemLoader(item=Airbnb_Calendar(), response=response)
        l.add_value('id', item_id)
        l.add_value('json', response.body)
        yield l.load_item()

    def parse_plus_detail(self, response):
        url_re = re.findall('/rooms(/plus)?/(.*)\?', response.url)[0]
        item_id = url_re[1]

        json_str = response.xpath('//script[@data-state]/text()').extract_first()
        if json_str[:4] == u'<!--':
            json_str = json_str[4:-3]

        json_obj = json.loads(json_str.encode('utf8'))
        location = json_obj['bootstrapData']['reduxData']['homePDP']['listingInfo']['listing']['sectioned_description'][
            'neighborhood_overview']
        location2 = json_obj['bootstrapData']['reduxData']['homePDP']['listingInfo']['listing'][
            'nearby_airport_distance_descriptions']
        l = ItemLoader(item=Airbnb_Location(), response=response)
        l.add_value('id', item_id)
        l.add_value('location', location)
        l.add_value('location2', location2)
        yield l.load_item()  # 去修改plus中的位置信息

    def parse_detail(self, response):
        url_re = re.findall('\?|&roomId=(.*)&?', response.url)
        item_id = url_re[1]

        json_str = response.xpath('//script[@type="application/json"]/text()').extract_first()
        if json_str[:4] == u'<!--':
            json_str = json_str[4:-3]

        location = None
        try:
            json_obj = json.loads(json_str.encode('utf8'))
            location = json_obj['ugcDescription']['original']['space']
        except Exception as ex:
            location = 'None'

        l = ItemLoader(item=Airbnb_Location(), response=response)
        l.add_value('id', item_id)
        l.add_value('location', location)
        yield l.load_item()

    #
    def parse(self, response):
        href_selector_arr = response.css('a._1yc2v57')
        hit_current_parse = []

        self.logger.info('[info]parse' + response.url)

        for href_node in href_selector_arr:
            item_id = re.findall('/rooms(/plus)?/(.*)\?', href_node.xpath('@href').extract()[0])[0][1]
            hit_current_parse.append(item_id)
            item_existed = self.db['airbnb'].find_one({"id": item_id})
            link = None

            if item_existed is None:
                l = ItemLoader(item=AirbubIdx(), response=response)
                l.add_value('link', href_node.xpath('@href').extract())
                l.add_value('label1', href_node.xpath('./div[2]')[0].xpath('./div/div/div/text()').extract())
                l.add_value('title', href_node.xpath('./div[2]/div[2]/text()')[0].extract())
                l.add_value('price', href_node.xpath('./div[3]//text()')[0].extract())
                l.add_value('id', item_id)
                yield l.load_item()  # 这个为了新建索引

            # 子页面
            link = response.urljoin(href_node.xpath('@href').extract_first())
            url_re = re.findall('/rooms(/plus)?/(.*)\?', link)[0]
            is_plus, item_id = url_re[0], url_re[1]

            # 这里为了更新位置信息
            if len(is_plus) > 0:
                # plus的信息跟进到下一个界面去请求
                yield scrapy.Request(link, callback=self.parse_plus_detail)
            else:
                # 没有plus的直接根据逻辑查第二次请求的页面
                param = ""
                if len(link.split('?')) == 2:
                    param = '?' + str(link.split('?')[1]) + '&roomId=' + item_id
                else:
                    param = '?roomId=' + item_id

                link = response.urljoin('/china-guest-moweb-loop/clr_result' + param)
                yield scrapy.Request(link, callback=self.parse_detail)

            # 这个是关键，去拿calendar
            calendar_api = self.generate_calendar_api_url(item_id)
            yield scrapy.Request(calendar_api, callback=self.parse_calendar_api)

        # 交集之后长度不一样，说明还是抓到新数据了
        array = list(set(self.hit_total) & set(hit_current_parse))
        if len(array) != len(hit_current_parse):
            next_url = self.url.replace('#{offset}', str(self.offset))
            self.offset += 20
            yield scrapy.Request(next_url, callback=self.parse)

        # 最后才把本次拿到的放进记录里
        for hint in hit_current_parse:
            self.hit_total.append(hint)
