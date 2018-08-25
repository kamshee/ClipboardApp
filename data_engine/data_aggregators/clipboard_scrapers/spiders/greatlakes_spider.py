# -*- coding: utf-8 -*-
from scrapy.spiders import Spider

from data_utils import DataUtils
from spider_base import SpiderBase


# greatlakes.org has an iCal feed: https://greatlakes.org/events/?ical=1&tribe_display=list
# Parsing that instead of the website would fix many of the imperfections of this scraper.
class GreatLakesSpider(Spider, SpiderBase):
    name = 'greatlakes'
    allowed_domains = ['greatlakes.org']

    def __init__(self, start_date, end_date):
        Spider.__init__(self)
        SpiderBase.__init__(self, 'https://greatlakes.org/', start_date, end_date, date_format='%B %d',
                            request_date_format='%Y-%m-%d')

    def start_requests(self):
        yield self.get_request('events/', {})

    def parse(self, response):
        # parser_factory = ParserFactory(response, 'Alliance for the Great Lakes')

        # parser.extract('.tribe-event-url').save('title')
        # parser.extract('.tribe-event-url::attr(href)').save('url')
        # parser.extract('.tribe-event-schedule-details').split('@').save('date', 'time_range')
        # parser.extract('.tribe-address').map(DataUtils.remove_excess_spaces).save('address')
        # parser.extract('.tribe-events-list-event-description').save('description')
        
        # return parser.create_events()

        parser = self.create_parser(response)
        titles = parser.parse('title', '.tribe-event-url')
        urls = parser.parse('url', '.tribe-event-url', extract_func=lambda i: i.attr('href'))
        dates, time_ranges = parser.parse_multiple(
            {'date': lambda s: s.split('@')[0], 
            'time_range': lambda s: s.split('@')[1]}, 
            '.tribe-event-schedule-details', iter_children=True)
        addresses = parser.parse('address', '.tribe-address', iter_children=True)
        descriptions = parser.parse('description', '.tribe-events-list-event-description', iter_children=True)

        return self.create_events('Alliance for the Great Lakes', titles, urls, dates, time_ranges, addresses, descriptions)

        # titles = self.extract('title', response.css, '.tribe-event-url::text')
        # urls = self.extract('url', response.css, '.tribe-event-url::attr(href)')
        # dates, time_ranges = self.extract_multiple(
        #     {'date': lambda s: s.split('@')[0], 
        #     'time_range': lambda s: s.split('@')[1]}, 
        #     response.css, '.tribe-event-schedule-details')
        # dates.remove_html()
        # time_ranges.remove_html()
        # addresses = self.extract('address', response.css, '.tribe-address').remove_html().map(
        #     DataUtils.remove_excess_spaces)
        # descriptions = self.extract('description', response.css, '.tribe-events-list-event-description').remove_html()

        # return self.create_events('Alliance for the Great Lakes', titles, urls, dates, time_ranges, addresses, descriptions)
