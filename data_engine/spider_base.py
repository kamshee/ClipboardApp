import scrapy
from urllib import parse
from pyquery import PyQuery
from aggregator_base import AggregatorBase
from event import Event, EventFieldData

# class EventStore(dict):
#     def __init__(self, date_format):
#         self.date_format = date_format

#     def create_events(self):
#         key_list = list(self.keys)
#         initial_count = len(self[key_list[0]])
#         for key, value in self.values:
#             if len(value) != initial_count:
#                 # All selectors must return the same amount of data because it's impossible to know which event is missing data otherwise
#                 raise ValueError('Selectors returned data of differing lengths')

#         events = (Event.from_dict({arg.item: arg.data[i] for arg in args}, self.time_utils.date_format) for i in range(count))
#         for event in events:
#             # Only return events that are in the date range that we care about
#             if self.time_utils.time_range_is_between(event['start_timestamp'], event['end_timestamp'], self.start_timestamp, self.end_timestamp):
#                 event['organization'] = organization
#                 yield event

# class ParserFactory:
#     def __init__(self, response, title, date_format):
#         self.response = response
#         self.title = title
#         self.event_store = EventStore(date_format)
    
#     def create(self):
#         return EventParser(self.response, self.title, self.event_store)

#     def create_events(self):
#         return self.event_store.create_events()

# class EventParser:
#     def __init__(self, response, title, event_store):
#         self.pq = PyQuery(response.body)
#         self.title = title
#         self.event_store = event_store
#         self.data = None

#     def extract(self, selector):
#         self.data = self.pq(selector)
#         return self

#     def text(self):
#         self.data = data.text() for data in self.data()
#         return self

#     def save(self):
#         self.event_store[self.title] = self.data

class EventParser:
    def __init__(self, response):
        self.pq = PyQuery(response.body)

    def text_extract(self, html_object):
        try:
            return html_object.text()
        except (ValueError, TypeError):
            return html_object.text

    def basic_extract(self, selector, extract_func, selector_func, transform_func, iter_children):
        if extract_func == 'default':
            extract_func = self.text_extract

        if selector_func != None:
            pq_parsed = selector_func(self.pq(selector))
        else:
            pq_parsed = self.pq(selector)

        if iter_children:
            pq_parsed = pq_parsed.items()    

        if extract_func != None:
            pq_parsed = [extract_func(PyQuery(i)) for i in pq_parsed]
        
        if transform_func != None:
            pq_parsed = transform_func(pq_parsed)

        return pq_parsed

    def parse(self, name, selector, extract_func='default', selector_func=None, transform_func=None, iter_children=False):
        return EventFieldData(name, self.basic_extract(selector, extract_func, selector_func, transform_func, iter_children))

    def parse_multiple(self, name_funcs, selector, extract_func='default', selector_func=None, transform_func=None, iter_children=False):
        pq_parsed = self.basic_extract(selector, extract_func, selector_func, transform_func, iter_children)
        for name in name_funcs.keys():
            yield EventFieldData(name, list(map(lambda i: name_funcs[name](i), pq_parsed)))


class SpiderBase(AggregatorBase):
    # This class includes all functionality that should be shared by spiders

    def __init__(self, base_url, start_date, end_date, date_format, request_date_format = None):
        super().__init__(base_url, start_date, end_date, date_format, request_date_format)

    def create_parser(self, response):
        return EventParser(response)
    
    def get_request(self, url, request_params):
        return scrapy.Request(f'{self.base_url}{url}?{parse.urlencode(request_params)}')

    def extract(self, name, extractor, path):
        # Remove leading and trailing whitespace from all extracted values
        return EventFieldData(name, list(map(lambda s: s.strip(), extractor(path).extract())))
    
    def pyquery_parse(self, response, selector):
        return PyQuery(response)(selector)

    def pyquery_extract(self, name, response, selector):
        data = self.pyquery_parse(response, selector)
        return EventFieldData(name, data)

    def pyquery_extract_multiple(self, name_funcs, data):
        data = self.pyquery_parse
        for name in name_funcs.keys():
            yield EventFieldData(name, map(lambda s: name_funcs[name](s), data))
            
    def re_extract(self, name, extractor, path, pattern):
        """
        Use this method to apply a regex filter to the extracted data

        :param name: The name of the event property extracted by this selector\n
        :param extractor: either response.css or response.xpath\n
        :param path: css or xpath selector string\n
        :param pattern: regex string to extract\n
        :returns: new EventFieldData object with the extracted data
        """
        return EventFieldData(name, list(map(lambda s: s.strip(), extractor(path).re(pattern))))

    def extract_multiple(self, name_funcs, extractor, path):
        """
        This method is necessary when there are multiple fields contained within a single xpath selector (e.g. a date and a time).
        name_funcs should be a dictionary in which the keys are event property names and the values are functions that extract
        the value that matches that key.

        :param name_funcs: A dictionary whose keys are the names of event properties and values are functions which take in a single string (the extracted value)
        and return the portion of the extracted value which represents the event property named in the key\n
        :param extractor: either response.css or response.xpath\n
        param path: css or xpath selector string\n
        :returns: a generator yielding each EventFieldData object with the extracted data
        """
        for name in name_funcs.keys():
            yield EventFieldData(name, list(map(lambda s: name_funcs[name](s).strip(), extractor(path).extract())))
    
    def empty_check_extract(self, name, base_selector, extractor_name, path, default_value=''):
        """
        Search for all values that match the xpath or css selector within the base selector and add a default value if nothing is found.
        Scrapy's selectors don't add anything to the response array if no value is found, so this
        method is necessary for semi-structured html blocks where a field could be missing.

        :param name: The name of the event property extracted by this selector\n
        :param base_selector: result of response.css or response.xpath call that contains the data to be processed further\n
        :param extractor_name: 'css' or 'xpath' depending on if the path variable is a css or xpath string\n
        :param path: css or xpath selector string\n
        :param default_value: What to return when the value isn't found in the selector\n
        :returns: new EventFieldData object with the extracted data
        """
        data = []
        for base_data in base_selector:
            extracted_data = eval(f'base_data.{extractor_name}(path).extract()')
            # Add a placeholder value if nothing was found on the site
            if len(extracted_data) == 0:
                extracted_data = [default_value]
            data.extend(extracted_data)
        
        return EventFieldData(name, data)

    def create_events(self, organization, *args):
        """
        Call this function once all of the data from the site has been extracted into variables

        :param organization: Name of the organization that owns the site\n
        :param *args: All EventFieldData objects generated by the extract methods in this class
        :returns: Generator yielding Event objects created from the EventFieldData objects
        """
        count = len(args[0].data)
        for arg in args:
            if len(arg.data) != count:
                # All selectors must return the same amount of data because it's impossible to know which event is missing data otherwise
                raise ValueError('Selectors returned data of differing lengths')

        events = (Event.from_dict({arg.item: arg.data[i] for arg in args}, self.time_utils.date_format) for i in range(count))
        for event in events:
            # Only return events that are in the date range that we care about
            if self.time_utils.time_range_is_between(event['start_timestamp'], event['end_timestamp'], self.start_timestamp, self.end_timestamp):
                event['organization'] = organization
                yield event
            

