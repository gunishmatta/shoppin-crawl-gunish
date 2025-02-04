import asyncio
import logging
import re
from typing import Optional, Set
from urllib.parse import urljoin, urlparse, urlunparse


from aiohttp import ClientSession, ClientTimeout
from bs4 import BeautifulSoup

from core.config import Config
from core.fetchers import FetcherFactory
from core.observer import Subject, LoggerObserver
from core.retry import retry
from core.utils import _find_next_page_by_query_parameter, _find_next_page_from_sibling_navigation, \
    _find_next_page_from_text_or_aria_label, _find_next_page_from_button_class, _find_next_page_from_seo_hint

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CrawlerService:
    def __init__(self):
        self.domains = []
        self.results = {}
        self.subject = Subject()
        self.subject.attach(LoggerObserver())
        self.domain_semaphores = {}
        self.sem = asyncio.Semaphore(500)


    async def crawl_all_domains(self, domains):
        """
        Crawl all domains concurrently using asyncio.
        """
        self.subject.notify("Starting crawl process...")
        try:
            tasks = [self.crawl_domain(domain) for domain in domains]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful_results = {}
            for domain, result in zip(domains, results):
                if isinstance(result, Exception):
                    self.subject.notify(f"Error crawling {domain}: {str(result)}")
                else:
                    successful_results[domain] = result
            self.results.update(successful_results)
            self.subject.notify(f"Crawl process completed. Successfully crawled {len(successful_results)} domains.")
            return self.results
        except Exception as e:
            self.subject.notify(f"Unexpected error during crawl process: {str(e)}")
            raise

    async def crawl_domain(self, domain: str):
        """
        Crawl a single domain and extract product URLs.
        """
        if domain not in self.domain_semaphores:
            self.domain_semaphores[domain] = asyncio.Semaphore(50)

        fetcher = FetcherFactory.get_fetcher(domain)
        product_urls = set()
        visited_urls = set()
        await self.crawl_page(domain, domain, visited_urls, product_urls, fetcher)
        self.subject.notify(f"Finished crawling {domain}. Found {len(product_urls)} product URLs.")
        return list(product_urls)

    @retry(max_retries=3, delay=2)
    async def crawl_page(self, domain: str, url: str, visited_urls: set, product_urls: set, fetcher):
        """
        Crawl a single page and extract product URLs.
        """
        if url in visited_urls:
            return
        visited_urls.add(url)

        content = await fetcher.fetch_content(url)
        if not content:
            self.subject.notify(f"No content found for URL: {url}")
            return
        urls = await self.extract_product_urls(domain, content)
        product_urls.update(urls)
        next_page_url = self.get_next_page_url(domain, content)
        if next_page_url:
            self.subject.notify(f"Found next page: {next_page_url}")
            await self.crawl_page(domain, next_page_url, visited_urls, product_urls, fetcher)

    def get_next_page_url(self, base_url: str, content: str) -> Optional[str]:
        """
        Extracts the URL of the next page from the given HTML content.
        """
        soup = BeautifulSoup(content, 'html.parser')
        strategies = [
            _find_next_page_from_seo_hint,
            _find_next_page_from_button_class,
            _find_next_page_from_text_or_aria_label,
            _find_next_page_from_sibling_navigation,
            _find_next_page_by_query_parameter,
        ]
        for strategy in strategies:
            next_page_url = strategy(soup) if 'soup' in strategy.__code__.co_varnames else strategy(base_url)
            if next_page_url:
                return self.generate_full_url(base_url, next_page_url)
        return None

    @staticmethod
    def generate_full_url(base_url: str, relative_url: str) -> str:
        """Generates a full URL by combining a cleaned base URL and a matched relative URL."""
        if not base_url.startswith(("http://", "https://")):
            base_url = "https://" + base_url

        parsed_base = urlparse(base_url)
        clean_base_url = urlunparse((parsed_base.scheme, parsed_base.netloc, '', '', '', ''))

        full_url = urljoin(clean_base_url, relative_url.lstrip('/'))
        return full_url

    async def extract_product_urls(self, domain: str, content: str) -> Set[str]:
        """Extract potentially valid product URLs from the content asynchronously."""
        urls = set()
        soup = BeautifulSoup(content, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']
            if any(re.search(pattern, href) for pattern in Config.DEFAULT_PRODUCT_PATTERNS):
                full_url = self.generate_full_url(domain, href)
                if not any(full_url.endswith(ext) for ext in ['.jpg', '.png', '.gif', '.jpeg']):
                    urls.add(full_url)

        valid_urls = set()
        async with ClientSession() as session:
            validation_tasks = [self.validate_url(session, url) for url in urls]
            results = await asyncio.gather(*validation_tasks)
            for url, is_valid in zip(urls, results):
                if is_valid:
                    valid_urls.add(url)
                else:
                    logging.debug(f"URL {url} was not valid or not a product page.")

        if not valid_urls:
            urls = await self.handle_unknown_patterns(domain, content)
            valid_urls.update(urls)
        return valid_urls

    @retry(max_retries=3, delay=2)
    async def validate_url(self, session: ClientSession, url: str) -> bool:
        """Validate if the URL is accessible and returns status code 200."""
        try:
            async with self.sem, session.get(url, timeout=ClientTimeout(total=10, connect=5),
                                             allow_redirects=True) as response:
                if response.status == 200:
                    content = await response.text()
                    if re.search(r'(product|item|details|description|itm|p)', content, re.IGNORECASE):
                        return True
        except Exception as e:
            logging.warning(f"Could not validate URL {url}: {str(e)}")
        return False

    async def handle_unknown_patterns(self, domain: str, content: str) -> Set[str]:
        """Handle cases for new or unknown product URL formats with validation."""
        urls = set()
        soup = BeautifulSoup(content, 'html.parser')
        async with ClientSession() as session:
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = self.generate_full_url(domain, href)
                if full_url.lower().endswith(('.jpg', '.png', '.gif', '.jpeg')):
                    continue
                if not any(re.search(pattern, href) for pattern in Config.DEFAULT_PRODUCT_PATTERNS):
                    if await self.validate_url(session, full_url):
                        urls.add(full_url)
                        logging.debug(f"Added unknown pattern URL: {full_url}")
        if urls:
            logging.info(f"Detected new URL patterns for domain: {domain}")

        return urls


