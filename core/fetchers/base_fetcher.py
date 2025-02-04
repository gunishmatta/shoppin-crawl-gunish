from abc import ABC, abstractmethod
import asyncio

class BaseFetcher(ABC):
    @abstractmethod
    async def fetch_content(self, url: str) -> str:
        """Fetch page content given a URL."""
        pass