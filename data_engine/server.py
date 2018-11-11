from flask import Flask, request, jsonify, Response, make_response

from apis.library_events import LibraryEvents
from apis.greatlakes_ical import GreatLakesReader
from clipboard_scrapers.spiders.history_spider import HistorySpider
from clipboard_scrapers.spiders.wpbcc_spider import WpbccSpider
from clipboard_scrapers.spiders.lwvchicago_spider import LWVchicago
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from dateutil.relativedelta import relativedelta
from klein import Klein

from scrapy import signals
from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy.settings import Settings

import os

#app = Flask(__name__)
app = Klein()

def spider_closing(spider):
    """Activates on spider closed signal"""
    log.msg("Closing reactor", level=log.INFO)
    #reactor.stop()

@app.route('/runspider', methods=['POST'])
def run_spider():
    request_obj = request.get_json()
    spider_name = request_obj['name']

     # Look for one month of events for testing purposes
    start_date = datetime.now().strftime('%m-%d-%Y')
    end_date = (datetime.now() + relativedelta(months=+1)).strftime('%m-%d-%Y')
    #log.start(loglevel=log.DEBUG)
    settings = get_project_settings()
    #crawler = Crawler(eval(spider_name), settings)
    crawlerProcess = CrawlerProcess(get_project_settings())
    crawlerProcess.crawl(HistorySpider, start_date, end_date)
    crawlerProcess.start()
    crawlerProcess.join()
    # /c/Users/asche/Anaconda3/scripts/scrapy.exe runspider apis/library_events.py -a start_date=10-21-2018 -a end_date=11-21-2018
    # stop reactor when spider closes
    #crawler.signals.connect(spider_closing, signal=signals.spider_closed)

    #crawler.configure()
    #crawler.crawl()
    #crawler.start()
    #reactor.run()

if __name__ == '__main__':
    app.debug = True
    
    app.run('localhost', port=5000)