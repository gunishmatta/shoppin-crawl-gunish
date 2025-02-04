import aiohttp
from .base_fetcher import BaseFetcher

class StaticContentFetcher(BaseFetcher):


    async def fetch_content(self, url: str) -> str:
        """Fetch static content."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.text()
                    return ""
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return ""
