from scrapy import Spider, Request, FormRequest
from scrapy.http import HtmlResponse
from urllib.parse import urljoin, urlparse
import os, re, csv, json
from scrapy_app.items import DynamicItem
from scrapy_app.settings import ARTICLES_CSV

import logging


def extract_with_xpath(parent, css_list):
    css_selector = css_list[0]  # '.myid'
    if not css_selector:
        return []

    value_elements = parent.css(css_selector)
    extract_type = css_list[1]  # 'text'
    if extract_type == 'text':
        css_extract = 'text()'
    elif extract_type == 'text_descendant':
        css_extract = 'descendant-or-self::text()'
    else:
        css_extract = '@{a}'.format(a=extract_type)
    values_extracted = value_elements.xpath(css_extract).extract()

    if not values_extracted:
        return []

    return values_extracted

def get_articleNames():
    with open(ARTICLES_CSV, mode='r', encoding='utf-8') as f:
        articleNames = [r['Name'] for r in csv.DictReader(f)]
    return articleNames

class MySpider(Spider):
    def __init__(self, articleName, **kwargs):
        super(MySpider, self).__init__(**kwargs)
        self.articleName = articleName

class FirstSpider(MySpider):
    name = "amazon"
    id = 1

    def start_requests(self):
        template_url = "https://www.amazon.de/s/ref=nb_sb_noss?__mk_de_DE=%C3%85M%C3%85%C5%BD%C3%95%C3%91&url=search-alias%3Daps&field-keywords={}"
        # articleNames = get_articleNames()
        # logging.info(articleNames[1])

        # used_articleNames = []
        # for articleName in articleNames:
        #     if articleName in used_articleNames:
        #         pass
        #     else:
            # articleName = articleNames[0]
        url = template_url.format(self.articleName)
        logging.info(url)
        yield Request(url, meta={'articleName': self.articleName}, callback=self.parse_list_1)

    def parse_list_1(self, response):
        self.current_url = response.url
        meta = response.meta
        logging.info('PARSING LIST ONE. {}'.format(response.url))

        container = response.css('#rightContainerATF')

        urls = container.xpath("//*[contains(text(), 'neu')]/@href").extract()
        # logging.info(urls)
        # logging.info(len(urls))

        for url in urls:
            # url = urls[1]
            yield Request(url, meta=meta, callback=self.parse_list_2)

        try:
            css_list = ["#pagnNextLink", "href"]
            next_link = extract_with_xpath(response, css_list)[0]
            logging.info('NEXT-LINK')
            yield Request(urljoin(self.current_url, next_link), callback=self.parse_list_1, meta=meta)
        except Exception as ex:
            logging.info(ex)

    def parse_list_2(self, response):

        self.current_url = response.url
        meta = response.meta
        logging.info('PARSING LIST TWO. {}'.format(response.url))

        urls = response.xpath("//*[contains(text(), 'Verkäuferinformationen')]/@href").extract()

        # logging.info(urls)
        # logging.info(len(urls))

        for url in urls:
            # url = urls[0]
            yield Request(urljoin(self.current_url, url), callback=self.parse_contactPage, meta=meta)

        try:
            css_list = [".a-last a", "href"]
            next_link = extract_with_xpath(response, css_list)[0]
            # logging.info('NEXT-LINK')
            yield Request(urljoin(self.current_url, next_link), callback=self.parse_list_2, meta=meta)
        except Exception as ex:
            logging.info(ex)

    def parse_contactPage(self, response):
        item = DynamicItem(url=response.url)
        item['article_name'] = response.meta['articleName']
        item['contact_center'] = response.xpath('//title/text()').extract()[0]
        item['contact_detail'] = " ,".join(extract_with_xpath(response, ["#aag_detailsAbout", "text_descendant"]))

        return item


class SecondSpider(MySpider):
    name = "rakuten"
    id = 2

    def start_requests(self):
        # articleNames = get_articleNames()
        # logging.info(articleNames[1])

        # used_articleNames = []
        # for articleName in articleNames:
        #     if articleName in used_articleNames:
        #         pass
        #     else:
        #         # articleName = articleNames[0]
        meta = {}
        url = "http://www.rakuten.de/rakuten-ajax/productlist/"
        data = {'filters[baseUrl]': url, 'filters[type]': 'search', 'filters[order_by]': '2',
                'filters[page]': '1',
                'filters[search_term]': self.articleName}
        meta['data'] = data
        meta['url'] = url
        meta['articleName'] = self.articleName
        # meta['page_number'] = 0
        yield FormRequest(url, callback=self.parse_list, formdata=data, meta=meta)

        # used_articleNames.append(articleName)

    def parse_list(self, response):
        self.current_url = response.url
        meta = response.meta
        logging.info('PARSING LIST ONE. {}'.format(response.url))

        parts = re.findall(r'a href.+?>', str(response.body))
        urls = [re.search('http.+?"', part).group().replace("\\", '').strip('"') for part in parts if
                'product-link' in part]

        for url in urls:
            yield Request(url, callback=self.parse_productPage, meta=meta)

        if len(urls) > 0:
            data = meta['data']
            data['filters[page]'] = str(int(data['filters[page]']) + 1)
            meta['data'] = data
            url = meta['url']
            yield FormRequest(url, callback=self.parse_list, formdata=data, meta=meta)

    def parse_productPage(self, response):

        self.current_url = response.url
        meta = response.meta
        logging.info('PARSING LIST TWO. {}'.format(response.url))

        item_Title = ''.join(response.css('title::text').extract()).split('|')[0].strip()
        meta['itemTitle'] = item_Title

        try:
            contact_link = response.xpath("//*[contains(text(), 'Kundeninformation')]/@href").extract()[0]
            yield Request(contact_link, callback=self.parse_contactPage, meta=meta)
        except Exception as ex:
            logging.info(ex)

    def parse_contactPage(self, response):
        parsed_uri = urlparse('http://stackoverflow.com/questions/1234567/blah-blah-blah-blah')
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        item = DynamicItem(url=response.url)
        item['article_name'] = response.meta['articleName']
        # item['item_title'] = response.meta['itemTitle']
        item['contact_center'] = urlparse(response.url).netloc
        item['contact_detail'] = " ,".join(extract_with_xpath(response, ["i", "text_descendant"]))

        return item


class ThirdSpider(MySpider):
    name = "ladenzeile"
    id = 3

    def start_requests(self):
        logging.info(self.name)
        template_url = "http://www.ladenzeile.de/suche?q={}"
        # articleNames = get_articleNames()
        # articleNames = ['shuhe']
        #
        # used_articleNames = []
        # for articleName in articleNames:
        #     if articleName in used_articleNames:
        #         pass
        #     else:
                # articleName = articleNames[0]
        url = template_url.format(self.articleName)
        logging.info(url)
        yield Request(url, meta={'articleName': self.articleName}, callback=self.parse_list)

    def parse_list(self, response):
        self.current_url = response.url
        meta = response.meta
        logging.info('PARSING LIST . {}'.format(response.url))
        container = response.css('body')

        shop_ids = [x.split(';')[0].split('(')[-1].split(',') for x in extract_with_xpath(container, [".item-info", "onclick"])]
        # logging.info(shop_ids)
        for shop_id in shop_ids:
        # shop_id = shop_ids[2]
            url = "http://www.ladenzeile.de/controller/cpac"
            data = {'i':shop_id[0], 'ts':shop_id[1]}
            yield FormRequest(url, callback=self.parse_json, formdata=data, meta=meta)

    def parse_json(self, response):
        meta = response.meta
        json_data = json.loads(response.body_as_unicode().replace('&&&VMBLABLA&&&', ''))
        # logging.info(json_data)
        shop_domain = json_data['shop']
        meta['shop'] = shop_domain.split('.')[0]
        url = ("http://www." + shop_domain).lower()
        # logging.info(url)

        yield Request(url, callback=self.parse_shopPage, meta=meta)

    def parse_shopPage(self, response):
        meta = response.meta
        logging.info('shopPage')
        logging.info(response.url)
        # logging.info(str(response.body))
        with open('html.txt', 'wb') as f:
            f.write(response.body)

        try:
            contact_link = urljoin(response.url, response.xpath("//*[contains(text(), 'mpressum')]/@href|//*[contains(text(), 'MPRESSUM')]/@href").extract()[0])
            # contact_link = "http://www.emilialay.de/impressum?cartid=572018635105235301679179"
            logging.info(contact_link)
            yield Request(contact_link, meta=meta, callback=self.parse_contactPage)
        except Exception as ex:
            logging.error(ex)

    def parse_contactPage(self, response):
        item = DynamicItem(url=response.url)
        item['article_name'] = response.meta['articleName']
        item['contact_center'] = response.meta['shop']
        raw_contactDetail = " ".join(response.xpath("body//*[contains(text(), 'mpressum') and not(self::script) and not(self::a)]/../descendant-or-self::text()|body//*[contains(text(), 'MPRESSUM') and not(self::script) and not(self::script)]/../descendant-or-self::text()").extract())
        item['contact_detail'] = re.sub('[a-z]mpressum', '', raw_contactDetail, flags=re.IGNORECASE)

        return item
