import urllib.parse as urlparse

import scrapy
from fix_price_scraper.config import COOKIES
from scrapy_playwright.page import PageMethod


class FixPriceSpider(scrapy.Spider):
    name = "fix_price"
    allowed_domains = ["fix-price.com"]
    BASE_URL = "https://fix-price.com"

    def __init__(self, categories=None, *args, **kwargs):
        if categories:
            self.category_urls = categories.split(", ")
        else:
            self.category_urls = []
        super().__init__(*args, **kwargs)

    async def handle_timeout(self, failure):
        self.logger.warning("Timeout occurred")
        request = failure.request
        page = request.meta.get("playwright_page")
        if page:
            try:
                await page.close()
            except Exception as e:
                self.logger.warning(f"Failed to close page in errback: {e}")

        retries = request.meta.get("retry_times", 0)
        if retries < 3:
            self.logger.info(f"Retrying {request.url}, attempt {retries + 1}")
            request.meta["retry_times"] = retries + 1
            yield request.replace(dont_filter=True)
        else:
            self.logger.error(f"Failed to load {request.url} after retries")

    def start_requests(self):
        for url in self.category_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div.product")],
                },
                callback=self.parse_category_page,
                cookies=COOKIES
            )

    async def parse_category_page(self, response):
        try:
            page = response.meta.get("playwright_page")
            if page:
                await page.close()
        except Exception as e:
            self.logger.warning(f"Failed to close page: {e}")

        section = response.css(
            ".crumb span[itemprop=\"name\"]::text"
        ).getall()[2:]

        parsed = urlparse.urlparse(response.url)
        query = urlparse.parse_qs(parsed.query)
        page = int(query.get("page", [1])[0])
        city = response.css(".top-wrapper .geo::text").get()
        self.logger.info(
            f"Section: {' > '.join(section)}, "
            f"page: {page}, "
            f"city: {city}"
        )

        for product in response.css("div.product"):
            relative_url = product.css("a::attr(href)").get()
            full_url = f"{self.BASE_URL}{relative_url}"
            yield scrapy.Request(
                full_url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod(
                            "wait_for_selector",
                            ".price-quantity-block .regular-price",
                            timeout=60000
                        )
                    ],
                    "section": section
                },
                callback=self.parse_product,
                cookies=COOKIES,
                errback=self.handle_timeout,
            )

        next_page = response.css(
            "a.button.active + a.button::attr(href)").get()
        if next_page:
            next_page_url = self.BASE_URL + next_page
            yield scrapy.Request(
                next_page_url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div.product")],
                },
                callback=self.parse_category_page,
                cookies=COOKIES
            )

    async def parse_product(self, response):
        try:
            page = response.meta.get("playwright_page")
            if page:
                await page.close()
        except Exception as e:
            self.logger.warning(f"Failed to close page: {e}")
