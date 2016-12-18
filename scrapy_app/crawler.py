from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor, defer
from pydispatch import dispatcher

from scrapy_app.spiders.spider import FirstSpider, SecondSpider, ThirdSpider

from scrapy_app.log import configure_logging

configure_logging()


# main class of the scraping project. "run_crawler" method for scraping sites from "client_ids" parameter.
class MainCrawler(object):
    def __init__(self,  *client_ids, max_items=None):  # client_ids - range or integer
        self.runner = CrawlerRunner(get_project_settings())
        if not client_ids:
            self.client_ids = range(1, 4)
        elif client_ids and type(client_ids[0]) == int:
            self.client_ids = client_ids
        elif type(client_ids[0]) != int:
            self.client_ids = client_ids[0]
        self.max_items = max_items
        self.spiders = {spider.id: spider for spider in [FirstSpider, SecondSpider, ThirdSpider]}
        self.spider = None
        self.ITEMS = []
        dispatcher.connect(receiver=self.add_item, signal=signals.item_scraped)

    def add_item(self, item):
        self.ITEMS.append(item)

    # main function for crawling. return dict of sites and items.
    def crawl(self):
        self.run_crawler()
        reactor.run()
        return self.ITEMS

    @defer.inlineCallbacks
    def run_crawler(self):
        for client_id in self.client_ids:
            json_settings = {}
            if client_id == self.client_ids[0]:
                json_settings['first_site'] = True
            self.spider = self.spiders[client_id]
            self.spider.custom_settings = {}
            if self.max_items: self.spider.custom_settings['CLOSESPIDER_ITEMCOUNT'] = self.max_items
            yield self.runner.crawl(self.spider, settings=json_settings)
        reactor.stop()

