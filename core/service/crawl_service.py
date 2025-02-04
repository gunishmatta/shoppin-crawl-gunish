import asyncio
import re
from typing import Optional

from bs4 import BeautifulSoup

from core.fetchers import FetcherFactory
from core.observer import Subject, LoggerObserver
from core.parsers.url_parsers import extract_product_urls, generate_full_url
from core.validators.url_validator import ImageURLValidation, ProductURLValidation, URLValidator


def _find_next_page_from_button_class(soup: BeautifulSoup) -> Optional[str]:
    next_button = soup.find('a', class_=re.compile(r'(s-pagination-next|pagination-next|btn-next|next)', re.IGNORECASE))
    return next_button['href'] if next_button and next_button.has_attr('href') else None


def _find_next_page_from_text_or_aria_label(soup: BeautifulSoup) -> Optional[str]:
    next_link = soup.find('a', string=re.compile(r'Next', re.IGNORECASE))
    next_link = next_link or soup.find('a', attrs={'aria-label': re.compile(r'next', re.IGNORECASE)})
    return next_link['href'] if next_link and next_link.has_attr('href') else None


def _find_next_page_from_seo_hint(soup: BeautifulSoup) -> Optional[str]:
    next_page_link = soup.find('link', rel='next')
    return next_page_link['href'] if next_page_link and next_page_link.has_attr('href') else None


def _find_next_page_from_sibling_navigation(soup: BeautifulSoup) -> Optional[str]:
    current_page = soup.find('span', class_=re.compile(r'pagination-selected', re.IGNORECASE))
    if current_page:
        parent = current_page.find_parent()
        next_sibling = current_page.find_next_sibling('a') if parent else None
        return next_sibling['href'] if next_sibling and next_sibling.has_attr('href') else None
    return None


def _find_next_page_by_query_parameter(base_url: str) -> Optional[str]:
    match = re.search(r'(page=)(\d+)', base_url)
    if match:
        current_page = int(match.group(2))
        next_page = current_page + 1
        return re.sub(r'(page=)\d+', f'page={next_page}', base_url)
    return None

class CrawlerService:
    def __init__(self):
        self.domains = []
        self.results = {}
        self.validator = URLValidator({
            "product": ProductURLValidation(),
            "image": ImageURLValidation()
        })
        self.subject = Subject()
        self.subject.attach(LoggerObserver())

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
        except Exception as e:
            self.subject.notify(f"Unexpected error during crawl process: {str(e)}")
            raise

    async def crawl_domain(self, domain: str):
        """
        Crawl a single domain and extract product URLs.
        """
        fetcher = FetcherFactory.get_fetcher(domain)
        product_urls = set()
        visited_urls = set()
        initial_url = f"https://{domain}"

        await self.crawl_page(domain, initial_url, visited_urls, product_urls, fetcher)
        self.subject.notify(f"Finished crawling {domain}. Found {len(product_urls)} product URLs.")
        return list(product_urls)

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

        urls = await extract_product_urls(domain, content)
        product_urls.update(urls)

        next_page_url = self.get_next_page_url(domain, content)
        if next_page_url:
            self.subject.notify(f"Found next page: {next_page_url}")
            await self.crawl_page(domain, next_page_url, visited_urls, product_urls, fetcher)

    @staticmethod
    def get_next_page_url(base_url: str, content: str) -> Optional[str]:
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
                return generate_full_url(base_url, next_page_url)
        return None



