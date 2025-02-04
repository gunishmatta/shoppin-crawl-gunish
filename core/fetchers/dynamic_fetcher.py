import asyncio

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from .base_fetcher import BaseFetcher

class DynamicContentFetcher(BaseFetcher):
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)

    def _get_page_source(self, url: str) -> str:
        self.driver.get(url)
        return self.driver.page_source

    async def fetch_content(self, url: str) -> str:
        """Fetch dynamic content."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._get_page_source, url)

    def __del__(self):
        self.driver.quit()
