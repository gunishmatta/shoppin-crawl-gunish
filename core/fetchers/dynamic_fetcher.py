import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from .base_fetcher import BaseFetcher

class DynamicContentFetcher(BaseFetcher):
    def __init__(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  
            chrome_options.add_argument("--disable-gpu") 
            chrome_options.add_argument("--no-sandbox")  
            chrome_options.add_argument("--disable-dev-shm-usage")  
            self.driver = webdriver.Chrome(options=chrome_options)
        except WebDriverException as e:
            print(f"Failed to initialize WebDriver: {e}")
            self.driver = None  

    def _get_page_source(self, url: str) -> str:
        if not self.driver:
            raise RuntimeError("WebDriver is not initialized")
        self.driver.get(url)
        return self.driver.page_source

    async def fetch_content(self, url: str) -> str:
        """Fetch dynamic content."""
        if not self.driver:
            raise RuntimeError("WebDriver is not initialized")
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._get_page_source, url)

    def __del__(self):
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()