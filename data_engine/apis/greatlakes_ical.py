from aggregator_base import AggregatorBase
from apis.ical_reader import ICal
from pytz import timezone
from scrapy.spiders import Spider
from api_base import ApiBase

class GreatLakesReader(Spider, ApiBase):
    name = 'great lakes'

    def parse(self, response):
        return self.get_events()

    def __init__(self, start_date, end_date):
        url = 'https://greatlakes.org/events/?ical=1&tribe_display=list'
        Spider.__init__(self)
        ApiBase.__init__(self, url, start_date, end_date, date_format='%Y-%m-%d')
        tz = timezone('America/Chicago')
        self.reader = ICal.from_url(self.base_url, tz)

    def get_events(self):
        return self.reader.parse_events()
        #self.save_events([event.to_dict() for event in events])
