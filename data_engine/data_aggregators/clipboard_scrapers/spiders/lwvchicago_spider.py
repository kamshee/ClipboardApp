# -*- coding: utf-8 -*-
import scrapy
#from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Spider
from event import Event
from categories import Category
from spider_base import SpiderBase

class LWVchicago(Spider, SpiderBase):
    name = 'lwvchicago'

    allowed_domains = ['my.lwv.org/illinois/chicago']

    def __init__(self, start_date, end_date):
        SpiderBase.__init__(self, 'https://my.lwv.org/illinois/chicago/', start_date, 
        	end_date, date_format = '%b %d %Y')

    def start_requests(self):
        yield self.get_request('calendar', {})

    def parse(self, response):
        parser = self.create_parser(response)
        titles = parser.parse('title', '.field.field-name-title', iter_children=True)
        dates, times = parser.parse_multiple(
            {'date': lambda s: s.split(' - ')[0], 
            'time': lambda s: s.split(' - ')[1] if len(s.split(' - ')) > 1 else ''}, 
            '.date-display-single', iter_children=True)
        addresses = parser.parse('address', '.field-label', selector_func=lambda i: i.siblings('p'))
        descriptions = parser.parse('description', '.text-secondary', iter_children=True)
        urls = parser.parse('url', '.field.field-name-title', selector_func=lambda i: i.items('a'), extract_func=lambda i: i.attr('href'))
        

        return self.create_events('League of Women Voters of Chicago', titles, times, dates, addresses, descriptions, urls)

