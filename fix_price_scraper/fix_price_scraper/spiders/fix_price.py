import scrapy


class FixPriceSpider(scrapy.Spider):
    name = "fix_price"
    allowed_domains = ["fix-price.com"]

    def parse(self, response):
        pass
