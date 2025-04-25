BOT_NAME = "fix_price_scraper"

SPIDER_MODULES = ["fix_price_scraper.spiders"]
NEWSPIDER_MODULE = "fix_price_scraper.spiders"


ROBOTSTXT_OBEY = False

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

LOG_LEVEL = 'INFO'
