import re
import logging
import asyncio
from typing import Set

from aiohttp import ClientSession, ClientTimeout
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse

from core.config import Config

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

sem = asyncio.Semaphore(100)


def generate_full_url(base_url: str, relative_url: str) -> str:
    """Generates a full URL by combining a cleaned base URL and a matched relative URL."""

    if not base_url.startswith(("http://", "https://")):
        base_url = "https://" + base_url

    parsed_base = urlparse(base_url)
    clean_base_url = urlunparse((parsed_base.scheme, parsed_base.netloc, '', '', '', ''))

    full_url = urljoin(clean_base_url, relative_url.lstrip('/'))
    return full_url


async def validate_url(session, url):
    """Validate if the URL is accessible and returns status code 200."""
    try:
        async with sem, session.get(url, timeout=ClientTimeout(total=10, connect=5), allow_redirects=True) as response:
            if response.status == 200:
                content = await response.text()
                if re.search(r'(product|item|details|description|itm|p)', content, re.IGNORECASE):
                    return True
    except Exception as e:
        logging.warning(f"Could not validate URL {url}: {str(e)}")
    return False


async def extract_product_urls(domain, content):
    """Extract potentially valid product URLs from the content asynchronously."""
    urls = set()
    soup = BeautifulSoup(content, 'html.parser')
    for link in soup.find_all('a', href=True):
        href = link['href']
        if any(re.search(pattern, href) for pattern in Config.DEFAULT_PRODUCT_PATTERNS):
            full_url = generate_full_url(domain, href)
            if not any(full_url.endswith(ext) for ext in ['.jpg', '.png', '.gif', '.jpeg']):
                urls.add(full_url)
    valid_urls = set()
    async with ClientSession() as session:
        validation_tasks = [validate_url(session, url) for url in urls]
        results = await asyncio.gather(*validation_tasks)
        for url, is_valid in zip(urls, results):
            if is_valid:
                valid_urls.add(url)
            else:
                logging.debug(f"URL {url} was not valid or not a product page.")
    if not valid_urls:
        valid_urls.update(await handle_unknown_patterns(domain, content))
    return valid_urls


async def handle_unknown_patterns(domain: str, content: str) -> Set[str]:
    """Handle cases for new or unknown product URL formats with validation."""
    urls = set()
    soup = BeautifulSoup(content, 'html.parser')
    async with ClientSession() as session:
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = generate_full_url(domain, href)
            if full_url.lower().endswith(('.jpg', '.png', '.gif', '.jpeg')):
                continue
            if not any(re.search(pattern, href) for pattern in Config.DEFAULT_PRODUCT_PATTERNS):
                if await validate_url(session, full_url):
                    urls.add(full_url)
                    logging.debug(f"Added unknown pattern URL: {full_url}")
    if urls:
        logging.info(f"Detected new URL patterns for domain: {domain}")

    return urls
