# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from event import Event
from categories import Category
from spider_base import SpiderBase

class WpbccSpider(CrawlSpider, SpiderBase):
    name = 'wpbcc'
    allowed_domains = ['www.wickerparkbucktown.com']

    rules = (
        Rule(LinkExtractor(restrict_css = ('.prevnextWindow', '.prevnextWindowArrow')), callback = 'parse_start_url', follow = True),
    )

    def __init__(self, start_date, end_date):
        CrawlSpider.__init__(self)
        SpiderBase.__init__(self, 'http://www.wickerparkbucktown.com/', start_date, end_date, date_format = '%B %d, %Y')

    def start_requests(self):
        yield self.get_request('events/', {
                'mrkrs': 'Chamber'
            })

    def parse_start_url(self, response):
        # base_selector = 'div/span[contains(text(), "{0}: ")]/following-sibling'
        # parser = EventParser(response, 'Wicker Park/Bucktown Chamber of Commerce')
        # parser.extract('.listerItem h2 a').text().save('title')
        # parser.extract('.listerItem h2 a::attr(href)').save('url')
        # parser.extract(['.listerContent', base_selector.format('Time')]).text().save('time')
        # parser.extract(['.listerContent', base_selector.format('Date')]).text().save('date')
        # parser.extract(['.listerContent'], base_selector.format('Address')).text().save('address')
        # parser.extract('.blurb').text().save('description')

        # return parser.create_events()
        def not_starts_with(string, values):
            return any(string.startswith(value) for value in values)

        def get_field(field, fields):
            filtered = [value for value in fields value.startswith(field)]
            return filtered[0] if filtered else ''

        def get_lister_content(selector_result, field):
            fields = selector_result.split('\n')
            if field == 'Time:':
                return get_field(field)
            if field == 'Address:'
                place = get_field('Place:')
                address = get_field('Address:')
                if place and address:
                    return f'{place}, {address}'
                return place or address

        def parse_lister_content(key, field):
            return parser.parse(key, '.listerContent', iter_children=True, transform_func=lambda i: get_lister_content(i, field))

        parser = self.create_parser(response)
        titles = parser.parse('title', '.listerItem h2 a')
        urls = parser.parse('url', '.listerItem h2 a', extract_func=lambda i: i.attr('href'))
        times = get_lister_content('time_range', 'Time:')
        dates = parser.parse('date', '.listerContent .date', iter_children=True, extract_func=lambda i: i.text().replace('Date: ', ''))
        addresses = get_lister_content('address', 'Address:')
        descriptions = parser.parse('description', '.listerContent .blurb', iter_children=True)

        # base_selector = response.css('.listerContent')
        
        # titles = self.extract('title', response.css, '.listerItem h2 a::text')
        # urls = self.extract('url', response.css, '.listerItem h2 a::attr(href)')
        # times = self.empty_check_extract('time_range', base_selector, 'xpath', 'div/span[contains(text(), "Time: ")]/following-sibling::text()')
        # dates = self.empty_check_extract('date', base_selector, 'xpath', 'div/span[contains(text(), "Date: ")]/following-sibling::text()')
        # addresses = self.empty_check_extract('address', base_selector, 'xpath', 'div/span[contains(text(), "Address: ")]/following-sibling::text()')
        # descriptions = self.extract('description', response.css, '.blurb::text')

        return self.create_events('Wicker Park/Bucktown Chamber of Commerce', titles, urls, times, dates, addresses, descriptions)
