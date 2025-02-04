import asyncio

import aiohttp
from .base_fetcher import BaseFetcher
from .dynamic_fetcher import DynamicContentFetcher
from .static_fetcher import StaticContentFetcher
from ..config import Config


class FetcherFactory:
    @staticmethod
    def get_fetcher(url: str) -> BaseFetcher:
        """Return appropriate fetcher based on page type."""
        if asyncio.get_event_loop().is_running():
            return DynamicContentFetcher()
        if FetcherFactory.is_dynamic_page(url):
            return DynamicContentFetcher()
        return StaticContentFetcher()

    @staticmethod
    async def is_dynamic_page(url: str) -> bool:
        """Heuristic to detect dynamic pages based on URL patterns."""
        if "?" in url or "#" in url:
            return True
        async def check_page_for_dynamic_content():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            return False
                        html_content = await response.text()
                        return any(pattern in html_content for pattern in Config.DYNAMIC_PAGE_PATTERNS)
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                return False
        return await check_page_for_dynamic_content()
