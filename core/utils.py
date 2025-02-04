import re
from typing import Optional

from bs4 import BeautifulSoup


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
