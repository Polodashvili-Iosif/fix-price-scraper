import logging
import re
import urllib.parse as urlparse

import httpx
import scrapy
from scrapy_playwright.page import PageMethod

from ..config import COOKIES, HEADERS, PARAMS
from ..models import AssetsData, PriceData, Product, StockData

logging.getLogger("httpx").setLevel(logging.WARNING)


class FixPriceSpider(scrapy.Spider):
    name = "fix_price"
    allowed_domains = ["fix-price.com"]
    BASE_URL = "https://fix-price.com"

    def __init__(self, categories=None, *args, **kwargs):
        self.httpx_client = httpx.AsyncClient()
        if categories:
            self.category_urls = categories.split(", ")
        else:
            self.category_urls = []
        super().__init__(*args, **kwargs)

    async def close(self, reason):
        await self.httpx_client.aclose()

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

    @staticmethod
    def get_price_data(response) -> dict:
        price_data = {
            "current": None,
            "original": None,
            "sale_tag": None,
        }
        if special_price := response.css(
                ".price-quantity-block .special-price::text"
        ).get():
            special_price = special_price.replace(",", ".")
            original_price = response.css(
                ".price-quantity-block .regular-price::text"
            ).get().replace(",", ".")
            price_data["original"] = float(original_price.split()[0])
            price_data["current"] = float(special_price.split()[0])
            discount_percentage = int(
                (1 - price_data["current"] / price_data["original"]) * 100
            )
            price_data["sale_tag"] = f"Скидка {discount_percentage}%"
        elif original_price := response.css(
                ".price-quantity-block .regular-price::text"
        ).get():
            price_data["original"] = float(
                original_price.replace(",", ".").split()[0]
            )
            price_data["current"] = price_data["original"]
        return price_data

    async def get_stock(self, rpc: str) -> dict:
        url = (
            f"https://api.fix-price.com/buyer/v1/store/balance/"
            f"{rpc}"
        )
        try:
            response_count = await self.httpx_client.get(
                url,
                params=PARAMS,
                headers=HEADERS,
                timeout=10.0
            )
            data = response_count.json()
            if not isinstance(data, list):
                raise ValueError("Unexpected response format")
        except Exception as e:
            self.logger.warning(f"Stock API error: {e}")
            data = []
        count = sum(store["count"] for store in data)
        return {
            "in_stock": bool(count),
            "count": count
        }

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
        data = {
            "metadata": {},
            "brand": None
        }

        properties = response.css(".properties .property")
        for item_property in properties:
            property_text = item_property.css(".title::text").get()
            property_value = item_property.css(".value::text").get()
            if property_text == "Бренд":
                property_value = item_property.css(".value a::text").get()
                data["brand"] = property_value
            elif property_text == "Код товара":
                data["RPC"] = property_value
            else:
                data["metadata"][property_text] = property_value
        data["metadata"]["__description"] = response.css(
            ".product-details .description::text"
        ).get()

        data["url"] = response.url
        data["title"] = response.css(
            "h1.title::text"
        ).get()
        if data["metadata"]["__description"]:
            for attribute in "Объём", "Цвет":
                pattern = rf"{attribute}: (\d+.+?)\."
                if match := re.search(
                    pattern, data["metadata"]["__description"]
                ):
                    value = match.group(1)
                    if value not in data["title"]:
                        data["title"] += f" {attribute}, {value}"
        self.logger.info(f"Item: {data['title']}")

        data["marketing_tags"] = response.css(
            ".price-quantity-block .sticker::text"
        ).getall()
        data["section"] = response.meta.get("section")

        data["price_data"] = self.get_price_data(response)

        data["stock"] = await self.get_stock(data['RPC'])

        data["assets"] = {
            "main_image": None,
            "view360": [],
            "video": []
        }
        data["assets"]["set_images"] = response.css(
            "img.normal::attr(src)").getall()
        if data["assets"]["set_images"]:
            data["assets"]["main_image"] = data["assets"]["set_images"][0]
        iframe_video_srcs = response.css(
            "iframe#rt-player::attr(src)"
        ).getall()
        if iframe_video_srcs:
            data["assets"]["video"] = [
                f"{iframe_video_src.replace('play/embed', 'video')}/"
                for iframe_video_src in iframe_video_srcs
            ]

        product = Product(
            metadata=data["metadata"],
            brand=data["brand"],
            RPC=data["RPC"],
            url=data["url"],
            title=data["title"],
            marketing_tags=data["marketing_tags"],
            section=data["section"],
            price_data=PriceData(**data["price_data"]),
            stock=StockData(**data["stock"]),
            assets=AssetsData(**data["assets"])
        )

        yield product.dict()
