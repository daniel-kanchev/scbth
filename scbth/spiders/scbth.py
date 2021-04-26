import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from scbth.items import Article
import requests
import json


class scbthSpider(scrapy.Spider):
    name = 'scbth'
    start_urls = ['https://www.scb.co.th/th/about-us/news.html']

    def parse(self, response):
        offset = 0
        json_response = json.loads(requests.get("https://www.scb.co.th/services/scb/articleFilter.json?_charset_=UTF-8&offset=0&lang=th&page=%2Fcontent%2Fscb%2Fth%2Fabout-us%2Fnews&categories=&dates=").text)
        total = json_response["total"]
        while offset < total:
            json_response = json.loads(requests.get(
                f"https://www.scb.co.th/services/scb/articleFilter.json?_charset_=UTF-8&offset={offset}&lang=th&page=%2Fcontent%2Fscb%2Fth%2Fabout-us%2Fnews&categories=&dates=").text)
            articles = json_response["result"]
            for article in articles:
                link = response.urljoin(article['linkUrl'])
                date = article["date"]
                yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))
            offset += 9

    def parse_article(self, response, date):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//p[@class="title-primary"]/text()').get() or response.xpath('//h2[@class="intro"]/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@id="wrappercomp"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
