from abc import ABC, abstractmethod
import asyncio

class BaseFetcher(ABC):
    @abstractmethod
    async def fetch_content(self, url: str) -> str:
        """Fetch page content given a URL."""
        pass

    async def retry(self, func, *args, **kwargs):
        """Retry a function upon failure."""
        retries = 3
        delay = 1
        for attempt in range(retries):
            try:
                return await func(*args, **kwargs)
            except (asyncio.TimeoutError, ConnectionError) as e:
                print(f"Attempt {attempt + 1} failed with error: {e}. Retrying in {delay}s...")
                await asyncio.sleep(delay)
                delay *= 2
        raise Exception("Failed to fetch content after retries")
