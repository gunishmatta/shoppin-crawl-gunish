import logging
import re
from abc import ABC, abstractmethod
from typing import Dict

from aiohttp import ClientTimeout


class URLValidationStrategy(ABC):
    @abstractmethod
    async def validate(self, session, url: str) -> bool:
        pass

class ProductURLValidation(URLValidationStrategy):
    async def validate(self, session, url: str) -> bool:
        try:
            async with session.get(url, timeout=ClientTimeout(total=10)) as response:
                if response.status == 200:
                    content = await response.text()
                    return bool(re.search(r'(product|item|details|description)', content, re.IGNORECASE))
        except Exception as e:
            logging.warning(f"Validation failed for {url}: {e}")
        return False

class ImageURLValidation(URLValidationStrategy):
    async def validate(self, session, url: str) -> bool:
        return not any(url.endswith(ext) for ext in ['.jpg', '.png', '.gif', '.jpeg'])

class URLValidator:
    def __init__(self, strategies: Dict[str, URLValidationStrategy]):
        self.strategies = strategies

    async def validate(self, session, url: str) -> bool:
        for strategy in self.strategies.values():
            if not await strategy.validate(session, url):
                return False
        return True