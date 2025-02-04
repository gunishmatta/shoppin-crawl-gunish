from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from .base_fetcher import BaseFetcher

class DynamicContentFetcher(BaseFetcher):
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)

    async def fetch_content(self, url: str) -> str:
        """Fetch dynamic content."""
        self.driver.get(url)
        return self.driver.page_source

    def __del__(self):
        self.driver.quit()
