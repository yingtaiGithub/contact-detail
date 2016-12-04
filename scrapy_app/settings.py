from os import path
SPIDER_MODULES = ['scrapy_app.spiders']

PROJECT_DIR = path.dirname(path.dirname(path.abspath(__file__)))
LOG_DIR = path.join(PROJECT_DIR, 'etc', 'logs')
ARTICLES_CSV = path.join(PROJECT_DIR, 'Article-list.csv')

MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017


ITEM_PIPELINES = {
    'scrapy_app.pipelines.Format': 200,
    'scrapy_app.pipelines.MongoDb': 900,
}

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) " \
             "Chrome/52.0.2743.116 Safari/537.36"

import logging
# LOG_ENABLED = True  # turn off default logger

# log fo file
logging.basicConfig(
    filename=path.join(path.join(PROJECT_DIR, 'etc'), 'log.txt'),
    filemode='w',
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)
#log to console
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(logging.Formatter(
    fmt='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
logging.getLogger().addHandler(console)
logging.getLogger("requests").setLevel(logging.WARNING)


# DOWNLOADER_MIDDLEWARES = {'scrapy_crawlera.CrawleraMiddleware': 300}
# CRAWLERA_ENABLED = False
# CRAWLERA_APIKEY = '81fb672d1e2d4d50a5fd5d95338ae849'